AI Powered GitHub PR Code reviewer 



Project based on Microservices:

\- Learner

\- Webhook

\- Orchestrator

\- Gateway

\- Reviewer



So, there will be 5 CI/CD pipeline (docker files)	



Overview of Project:

When you make a PR on GitHub, it will analyze the code and based on analysis it will give proper AI code review and line by line review of code on GitHub application. 

Application will be running AWS(EKS clusters, ECR repo, analyzing 5-9 secs for small code, 8-15 secs for bigger code). 

Redis for caching and queuing, salary workers for executing task and entire app will asynchronous to increase performance and reliability.

For monitoring and observability langfuse will be used. 



The application will have 4 ai agents:

\- For static code analysis (bugs, error)

\- Security

\- Style

\- Architecture analysis



For evaluation, RAGAS is used, postgres database is used. 

So in total there will 6 pipelines: 5 for microservices and 1 for LLM evaluation.





Problem Statement:

Assume a startup ( maybe fintech), employees are working so feature development, where they have the main repository. Assume there 2 senior developers and around 18-20 junior developers working on the feature. One of the junior developers, made some changes in his master branch and wanted to merge the change in the main repository. 

As junior developers might have made some mistakes, so these mistakes are verified by the senior developer by reviewing the code before merging the code into main repo. It is not feasible for senior developer to review each code. 

So the issue is : time, a review can be inconsistent as well, and human error as senior developer could also make mistake.

This issues are handled by this application.





Tech Stack:



LLM - OpenAi(gpt-4o)

Langgraph for creating ai agents

Langfuse for observability 



Backend:

\- FAST API (for async functions)

\- Celery for background processes(task queuing)

\- Redis (AWS Elastic cache) 

\- RDS (SQL db)

\- SQL alchemy

\- HTTPX makes async http calls

\- PyJWT to generate JWT tokens for authentication with GitHub



Infrastructure:

\- Terraform (Iaac Tool)

\- Docker

\- S3 buckets

\- ECR for storing docker images

\- Kubernetes Service (AWS EKS) 

\- GitHub Actions for CI/CD 

\- Kubectl for interacting with Kubernetes cluster

\- RAGAS 

\- Prometheus for extracting metrics Grafana for dashboard. So they will be used for monitoring of whole project

\- Alembic, a data migration tool

\- GitHub App

\- Cryptography (HMAC SHA 256) for verifying webhook requests. so it is basically a security check. in gateway So only requests coming from GitHub will be allowed and all the other requests coming from different sources will be rejected.







**Project Architecture:** 



* When a user creates a GitHub pull request, it will trigger an event.
* This request will hit a public url. Basically, GitHub will send a http request to webhook. That request will go through a load balancer. Load balancer is used for scalability and routing purpose. 
* After passing through load balancer, it will go to the first microservice i.e. gateway service (Fast API). Gateway service is basically a security layer, it will verify the request if its coming from GitHub or not. If yes, then forward the request, if not, reject the request.
* Once the request is forwarded, it will go to second microservice, i.e. webhook service. This webhook service is like a event processor. It will extract the PR number, the repo on which the PR was made, SHA number or verification signature, delete the duplicates by overriding SHA ( basically all the metadata). All the extracted metadata will be stored on SQL database.
* After going through the webhook service, it will go to the Redis queue, which is async system. With async system we can initiate multiple PR requests overlapping them after one another. In redis, the PR will be treated as a job and will create a queue for PRs.
* Celery will handle the execution of PR request(or job) in the background.
* Celery will send the job or request to the third microservice i.e. Orchestrator service. Orchestrator is the brain of the system
* All the ai agents will be inside the orchestrator service. Orchestrator will extract the code. Once the code has been fetched, ai agents will run on that code. The 4 ai agents will analyze the code and merge all the findings by each agent. It will also remove duplicate findings by the agent. All the findings will be stored in database.
* After going through orchestrator, it will go to the fourth microservice i.e. reviewer service. We want to display the findings on our GitHub applications, the reviewer service will generate JWT tokens and with those tokens will authenticate with GitHub and post the in-line comments on the GitHub pr, post the summary etc.
* After reviewer service, automatically GitHub pull request will be updated and developer can fix the code and push the changes into the main repo.
* If the code has any errors or changes, the PR will be merged directly into the main repo. After the PR has been merged, fifth microservice i.e. learner service will run.
* The learner service will store patterns of the error and other issues in the database. We want our AI agent to be smarter over the time.
* For DevOps, there will be 6 pipelines: 5 for microservice and 1 for LLM evaluation. 5 docker files, 5 ecr repo 











LangFuse API keys:



\- Secret Key: sk-lf-22519c1e-74f3-4845-aa83-004ec9231458

\- Public Key: pk-lf-76709943-d281-4b53-a7ba-5277fa6b5644





























