\# Cloud-Deployed Distributed Radiograph Processing System



\## Project 1 – Distributed Systems



\### Overview

This project implements a cloud-based distributed radiograph processing pipeline fully deployed on Amazon Web Services (AWS).



The system models a real-world medical imaging workflow with asynchronous job handling, durable storage, and scalable worker processing.



\### Architecture Components



\- \*\*API Server (EC2)\*\* – Flask REST API

\- \*\*Worker Node (EC2)\*\* – Kafka consumer \& image processor

\- \*\*Amazon MSK (Kafka)\*\* – Messaging backbone

\- \*\*Amazon S3\*\* – Input and output image storage

\- \*\*Amazon RDS PostgreSQL\*\* – Metadata persistence



No serverless functions, containers, or Kubernetes were used.



---



\## REST API Endpoints



\### POST /submit

Submit an image processing job.



Request body:

```json

{

&nbsp; "image\_key": "example.png"

}



GET /recent?n=10



Retrieve recent processed jobs.



GET /health



System health check.



Worker Process



The worker:



Consumes Kafka messages



Downloads image from S3 input bucket



Generates a bounding box overlay



Uploads processed image to S3 output bucket



Inserts job metadata into PostgreSQL



Environment Variables Required



KAFKA\_BOOTSTRAP

KAFKA\_USER

KAFKA\_PASS

DB\_HOST

DB\_USER

DB\_PASS

S3\_INPUT\_BUCKET

S3\_OUTPUT\_BUCKET



Deployment



Fully deployed and validated on AWS using:



EC2 instances



Amazon MSK cluster



Amazon S3 buckets



Amazon RDS PostgreSQL instance



See attached PDF report for infrastructure screenshots and validation evidence.

