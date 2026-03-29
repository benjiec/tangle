## Google Cloud Setup

Create project

Enable services
  * Batch API
  * Artifact Repository API
  * Compute Engine API
  * BigQuery API

Create service account for nextflow, e.g. nextflow-service-account@needle-489321.iam.gserviceaccount.com

Add roles to service account
  * Artifact Registry Reader
  * Batch Agent Reporter
  * BigQuery Data Editor
  * Storage Object Admin

Also, create a key for this service account, download the JSON key and put in ~/.config/gcloud

Some initialization stuff

```
gcloud init
gcloud auth application-default login
gcloud auth configure-docker us-east1-docker.pkg.dev
```

Create a docker repository

```
gcloud artifacts repositories create tangle-docker \
    --repository-format=docker \
    --location=us-east1 \
    --description="Docker repository for Tangle"
```

Create a bucket for storing files

```
gcloud storage buckets create gs://needle-files\
    --location=us-east1 \
    --uniform-bucket-level-access
```

And copy some files

```
gcloud storage cp -r hmm/\* gs://needle-files/hmm/
gcloud storage cp -r foldseek/\* gs://needle-files/foldseek/
```


## Building Images

For example, suppose you want to build and push the Docker image from the heap repo.

```
docker build --platform linux/amd64 -t us-east1-docker.pkg.dev/needle-489321/tangle-docker/heap:latest .
docker push us-east1-docker.pkg.dev/needle-489321/tangle-docker/heap:latest
```

Test the image

```
gcloud batch jobs submit test-job-v1 \
    --location us-east1 \
    --config - <<EOF
{
  "taskGroups": [
    {
      "taskSpec": {
        "runnables": [
          {
            "container": {
              "imageUri": "us-east1-docker.pkg.dev/needle-489321/tangle-docker/heap:latest",
              "commands": ["python3", "scripts/foldseek-swissprot.py"]
            }
          }
        ]
      },
      "taskCount": 1
    }
  ],
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}
EOF
```

Then you can look at the status of the job

```
gcloud batch jobs describe test-job-v1 --location us-east1
gcloud batch jobs delete test-job-v1 --location us-east1
```

If the image worked and ran, you should be able to see the standard argparse
based error message from the Google Cloud logging interface.
