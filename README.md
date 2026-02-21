# Cloud-Deployed Distributed Radiograph Processing System

## Project 1 – Distributed Systems

---

## Overview

This project implements a cloud-based distributed radiograph processing pipeline fully deployed on Amazon Web Services (AWS).

The system demonstrates:

- Asynchronous job submission  
- Decoupled event-driven architecture  
- Distributed message processing  
- Durable object storage  
- Relational metadata persistence  

The application simulates a radiograph processing workflow in a scalable and production-style architecture.

---

## Architecture Components

- **API Server (EC2)** – Flask REST API  
- **Worker Node (EC2)** – Kafka consumer & image processor  
- **Amazon MSK (Kafka)** – Messaging backbone  
- **Amazon S3** – Input and output image storage  
- **Amazon RDS PostgreSQL** – Metadata persistence  

No serverless functions, containers, or Kubernetes were used in this implementation.

---

## REST API Endpoints

### POST /submit

Submit an image processing job.

Request body:

```json
{
  "image_key": "example.png"
}
```

Response:

```json
{
  "queued": true,
  "topic": "rfo-jobs",
  "image_key": "example.png"
}
```

---

### GET /recent?n=10

Retrieve recent processed jobs from the PostgreSQL database.

---

### GET /health

Health check endpoint to verify API availability.

---

## Worker Processing Flow

The worker performs:

1. Consumes Kafka messages  
2. Downloads image from S3 input bucket  
3. Generates a bounding box overlay  
4. Uploads processed image to S3 output bucket  
5. Inserts job metadata into PostgreSQL  

---

## Environment Variables Required

```
KAFKA_BOOTSTRAP
KAFKA_USER
KAFKA_PASS
DB_HOST
DB_USER
DB_PASS
S3_INPUT_BUCKET
S3_OUTPUT_BUCKET
```

---

## Deployment

The system was fully deployed and validated on AWS using:

- EC2 instances
- Amazon MSK cluster
- Amazon S3 buckets
- Amazon RDS PostgreSQL

See the attached PDF report for infrastructure screenshots and execution validation evidence.



