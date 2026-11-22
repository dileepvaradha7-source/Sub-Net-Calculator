# IPv4 Subnet Calculator

Individual B9IS121 practical project: a stateless web app deployed from a Git commit through GitHub Actions, GitHub Container Registry and Render Free. The pipeline also publishes an image to Amazon ECR as an additional cloud registry demonstration.

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
  → Amazon ECR + GitHub Container Registry → Render deploy hook
  → Render Free pulls image → public HTTPS URL → browser and Postman
```

The workflow pushes both `latest` and commit-SHA tags for traceability. Render pulls the public `latest` image from GitHub Container Registry when GitHub Actions calls its deploy hook. The `GET /api/version` response exposes the built commit SHA.

## AWS and GitHub setup checklist

1. The AWS Free plan, ECR repository and branch-scoped GitHub OIDC role have been configured in `ap-southeast-2`. The first GitHub Actions run successfully tested, built and published the image to ECR.
2. App Runner returned an explicit AWS Organizations service-control-policy deny. The Free plan does not permit this service, so the public host is Render Free. Do not upgrade the AWS account.
3. Push this updated workflow to `main`. It publishes the same image to GitHub Container Registry at `ghcr.io/dileepvaradha7-source/sub-net-calculator:latest` and also retains the ECR publish stage.
4. In GitHub Packages, make the new container package **public**, so Render can pull it without a credential.
5. Create a **Free** Render web service from **Existing Image** using that GHCR image URL. Do not add a payment method or select paid compute. Set health check path `/health` if offered. The app listens on Render's `PORT` environment value.
6. In the Render service's Settings page, copy its **Deploy Hook URL** into the GitHub Actions secret `RENDER_DEPLOY_HOOK_URL`. Keep this URL private.
7. Add the Render HTTPS base URL as GitHub Actions variable `PUBLIC_APP_URL`.
8. Make a second visible source change, push to `main`, and show the new GitHub Actions run, Render deploy event and updated `/api/version` response. The workflow triggers Render through the deploy hook after the image push and waits until the live endpoint serves the new commit SHA.

Render Free spins down after 15 idle minutes and can take about a minute to wake. Open the app before recording or testing. Without a payment method, Render says free services are suspended if included bandwidth is exhausted. Keep the app available for the assessor.

## Postman requests

Use the public Render URL as `BASE_URL`.

| Method | URL | Body | Expected result |
| --- | --- | --- | --- |
| GET | `{{BASE_URL}}/health` | none | 200, `{"status":"ok"}` |
| GET | `{{BASE_URL}}/api/version` | none | 200, current commit SHA |
| POST | `{{BASE_URL}}/api/subnets` | JSON `{"cidr":"192.168.10.42/24"}` | 200, network `192.168.10.0/24`, 254 usable addresses |
| POST | `{{BASE_URL}}/api/subnets` | JSON `{"cidr":"999.1.1.1/24"}` | 400, validation error |

## Limits

The app calculates IPv4 subnet information only. It does not discover devices or monitor a real network. It stores no state. Render Free is limited to one instance and has an ephemeral filesystem. The public endpoints have no user accounts or request rate limits. App Runner was unavailable because of the AWS Free plan's service-control-policy deny.

## Evidence to capture

- GitHub repository and successful Actions run showing test, build and publish stages.
- ECR repository with `latest` and commit-SHA tags.
- Render deployment status and public URL.
- Postman request URL, status code and response body for success and invalid input.
- First and second commit SHA values, plus the updated live `/api/version` response.
- Actual connectivity issue and fix, if one occurs. Do not invent an issue.
- AWS App Runner access-denied error, explained as the reason for the documented cloud-host change.

## Primary documentation

- [Assignment PDF](B9IS121%20Network%20and%20Systems%20Admin%202027.pdf)
- [AWS App Runner deployment methods](https://docs.aws.amazon.com/apprunner/latest/dg/manage-deploy.html)
- [AWS App Runner ECR access role](https://docs.aws.amazon.com/apprunner/latest/dg/security_iam_service-with-iam.html)
- [AWS GitHub Actions credentials action](https://github.com/aws-actions/configure-aws-credentials)
- [AWS App Runner pricing](https://aws.amazon.com/apprunner/pricing/)
- [Render image-backed services](https://render.com/docs/deploying-an-image)
- [Render deploy hooks](https://render.com/docs/deploy-hooks)
- [Render Free limits](https://render.com/docs/free)
