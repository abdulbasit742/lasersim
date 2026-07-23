# LaserSim API Deployment

## Environment Variables

- LASERSIM_MODEL_PATH: path to trained model checkpoint
- LASERSIM_API_KEY: API authentication key
- LASERSIM_ENV: runtime environment

## Production Checklist

- Use environment secrets
- Run behind HTTPS proxy
- Enable monitoring
- Validate model checkpoints before deployment
