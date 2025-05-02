# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import firebase_admin
from firebase_functions import https_fn
from firebase_admin import db
import time  # noqa: F401

# Initialize Firebase Admin SDK ONCE.
# Cloud Functions automatically use the project's service account.
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    print("Firebase Admin SDK initialized successfully for Cloud Function.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK in Cloud Function: {e}")

# Define the database path for requests (adjust user ID handling as needed)
# For simplicity, using a fixed user ID here. You might pass it from the client.    # noqa: E501
USER_ID = "TObhhpC3JdSBFIkI6None92FN2Q2"
CAPTURE_REQUEST_PATH = f"users/{USER_ID}/captureRequests"


@https_fn.on_request()
def requestDataCapture(req: https_fn.Request) -> https_fn.Response:
    """
    HTTPS Cloud Function to signal a request for data capture by writing
    to the Realtime Database.
    """
    print(f"Received data capture request for user: {USER_ID}")

    # Add CORS headers directly to the response instead of using global options
    if req.method == "OPTIONS":
        # Handle preflight request
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return https_fn.Response("", status=204, headers=headers)

    # Set CORS headers for the main request
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }  # noqa: E501

    # --- Optional: Add Authentication/Authorization here ---
    # Verify Firebase Auth token, check user permissions, etc.
    # ---

    try:
        # Get a reference to the capture request location
        req_ref = db.reference(CAPTURE_REQUEST_PATH)

        # Push a new request entry with a timestamp
        # The listener will react to this new child entry
        new_request = req_ref.push(
            {
                "requestTimestamp": {".sv": "timestamp"},
                "status": "pending",
                "requestedFrom": "web",  # Or add more context if needed
            }
        )

        print(f"Capture request logged to DB at path: {new_request.path}")

        return https_fn.Response(
            '{"message": "Capture request successfully logged."}',
            status=200,
            headers=headers,
        )

    except Exception as e:
        print(f"Error logging capture request: {e}")
        return https_fn.Response(
            f'{{"message": "Internal server error: {str(e)}"}}',
            status=500,
            headers=headers,
        )
