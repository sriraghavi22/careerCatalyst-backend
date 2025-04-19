import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

def update_access_mode(folder='resumes'):
    try:
        next_cursor = None
        all_resources = []

        # Fetch all resources with pagination
        while True:
            params = {
                'resource_type': 'image',
                'type': 'upload',
                'prefix': folder,
                'max_results': 500,
                'next_cursor': next_cursor
            }
            response = cloudinary.api.resources(**params)
            resources = response.get('resources', [])
            all_resources.extend(resources)
            next_cursor = response.get('next_cursor')
            if not next_cursor:
                break

        if not all_resources:
            print(f"No resources found in folder '{folder}'")
            return

        for resource in all_resources:
            try:
                public_id = resource.get('public_id')
                if not public_id:
                    print(f"Skipping resource with missing public_id: {resource}")
                    continue

                # Handle missing or invalid access_mode
                current_access_mode = resource.get('access_mode', 'unknown')
                if current_access_mode not in ['public', 'authenticated', 'private']:
                    print(f"Invalid access_mode '{current_access_mode}' for {public_id}, assuming authenticated")
                    current_access_mode = 'authenticated'

                if current_access_mode != 'public':
                    print(f"Updating {public_id} from {current_access_mode} to public")
                    cloudinary.api.update(
                        public_id,
                        resource_type='image',
                        access_mode='public'
                    )
                    print(f"Updated {public_id} to public")
                else:
                    print(f"{public_id} is already public")
            except Exception as e:
                print(f"Error processing {public_id}: {str(e)}")
    except Exception as e:
        print(f"Error fetching resources: {str(e)}")

if __name__ == '__main__':
    update_access_mode()