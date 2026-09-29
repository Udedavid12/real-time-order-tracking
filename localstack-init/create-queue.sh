#!/bin/bash
echo "Creating SQS queue: location_updates"
awslocal sqs create-queue --queue-name location_updates
echo "Queue created."