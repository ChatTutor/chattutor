gcloud run deploy chattutor --source .

gcloud run services update chattutor --set-env-vars "CHATUTOR_GCP=TRUE" \
   --set-env-vars "OPENAI_API_KEY=<>" \
   --set-env-vars "ACTIVELOOP_TOKEN=<>"