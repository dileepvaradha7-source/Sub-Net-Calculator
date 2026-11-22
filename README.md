# IPv4 Subnet Calculator

Individual B9IS121 practical project: a stateless web app deployed from a Git commit through GitHub Actions, Amazon ECR and AWS App Runner.

Repository: https://github.com/dileepvaradha7-source/Sub-Net-Calculator

## Local use

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 app.py
```

Open `http://localhost:8080` or call:

```sh
curl -s http://localhost:8080/health
curl -s http://localhost:8080/api/version
curl -s -X POST http://localhost:8080/api/subnets \
  -H 'Content-Type: application/json' \
  -d '{"cidr":"192.168.10.42/24"}'
```

## Deployment design

```text
Developer commit → GitHub main branch → GitHub Actions tests and Docker build
  → Amazon ECR private repository → App Runner automatic image deployment
  → public HTTPS URL → browser and Postman
```

AWS App Runner must use an image in an **ECR private repository in the same AWS account** for its automatic image deployment. Configure it to watch the `latest` tag. The workflow also pushes a commit-SHA tag for traceability. The `GET /api/version` response exposes the built commit SHA.

## AWS and GitHub setup checklist

1. Confirm the AWS Billing console says **Free plan** and shows the available credit. Do not upgrade the account.
2. Use `ap-southeast-2` (Sydney) for ECR, App Runner and the GitHub Actions `AWS_REGION` variable.
3. Create an ECR **private** repository named `subnet-calculator`.
4. Add GitHub as an IAM OpenID Connect identity provider with URL `https://token.actions.githubusercontent.com` and audience `sts.amazonaws.com`.
5. Create an IAM role trusted only by this repository's `main` branch OIDC subject. Give it the minimum ECR permissions to authenticate and upload images to this repository. Follow the current GitHub and AWS instructions for the exact OIDC subject format, which can differ for newly created repositories.
6. In the GitHub repository, create Actions secret `AWS_ROLE_ARN` with that role ARN; create Actions variables `AWS_REGION` and `ECR_REPOSITORY` (`subnet-calculator`). Never put AWS keys in the repository.
7. Push to `main`. Watch the GitHub Actions run until tests, build, container smoke test and both ECR image pushes pass.
8. In App Runner, create a service from the ECR **private** image tagged `latest`. Choose **Automatic** deployment, create/select the App Runner ECR access role, set port `8080`, and choose the smallest suitable CPU/memory option. Keep scaling limits low to protect the credit balance.
9. Record the App Runner HTTPS URL as GitHub Actions variable `APP_RUNNER_URL`. The next workflow run will wait for that exact commit to appear on the live endpoint. Test `/`, `/health`, `/api/version` and `/api/subnets` with Postman.
10. Make a second visible source change, push to `main`, and show the new GitHub Actions run, App Runner deployment and updated `/api/version` response.

App Runner charges for provisioned memory while the service is idle. Monitor AWS Billing credit usage. Keep the app running until the assessor has had access to it; pause or delete resources afterward.

## Postman requests

Use the public App Runner URL as `BASE_URL`.

| Method | URL | Body | Expected result |
| --- | --- | --- | --- |
| GET | `{{BASE_URL}}/health` | none | 200, `{"status":"ok"}` |
| GET | `{{BASE_URL}}/api/version` | none | 200, current commit SHA |
| POST | `{{BASE_URL}}/api/subnets` | JSON `{"cidr":"192.168.10.42/24"}` | 200, network `192.168.10.0/24`, 254 usable addresses |
| POST | `{{BASE_URL}}/api/subnets` | JSON `{"cidr":"999.1.1.1/24"}` | 400, validation error |

## Limits

The app calculates IPv4 subnet information only. It does not discover devices or monitor a real network. It stores no state, so it can run on multiple stateless instances, but this demonstration uses conservative scaling limits. The public endpoints have no user accounts or request rate limits. App Runner, its image store and logs can use AWS credit even when the application receives little traffic.

## Evidence to capture

- GitHub repository and successful Actions run showing test, build and publish stages.
- ECR repository with `latest` and commit-SHA tags.
- App Runner deployment status and public URL.
- Postman request URL, status code and response body for success and invalid input.
- First and second commit SHA values, plus the updated live `/api/version` response.
- Actual connectivity issue and fix, if one occurs. Do not invent an issue.
- AWS Billing plan and credit status for cost evaluation (redact account number and personal details).

## Primary documentation

- [Assignment PDF](B9IS121%20Network%20and%20Systems%20Admin%202027.pdf)
- [AWS App Runner deployment methods](https://docs.aws.amazon.com/apprunner/latest/dg/manage-deploy.html)
- [AWS App Runner ECR access role](https://docs.aws.amazon.com/apprunner/latest/dg/security_iam_service-with-iam.html)
- [AWS GitHub Actions credentials action](https://github.com/aws-actions/configure-aws-credentials)
- [AWS App Runner pricing](https://aws.amazon.com/apprunner/pricing/)
