POJA CLI
========

A Python CLI to the [POJA stack](https://github.com/hei-school/poja).

## General usage

1. Invoke the [POJA CLI](https://pypi.org/project/poja/) depending on the use case you want to address, see section below. We recommend prefixing your poja application names with `poja-`.
2. Commit changes and push them to Github.
3. **(*)** Create two entries in SSM that stores the credentials of the database that will be created. The name MUST be as follows: `/<?app-name>/<?env>/db/username` and `/<?app-name>/<?env>/db/password` where `<?app-name>` is any name you want and `<?env>` is either `prod` or `preprod`.
4. **(*)** Define the Github variable `PROD_DB_CLUSTER_TIMEOUT` that sets the prod database cluster scaling down timeout. Note that its value must be between 300 seconds (5 minutes) and 86_400 seconds (1 day). Due to the once-per-day health check action, the (serverless) prod database will always be hot if you set it to one day.
5. Define the Github secrets for deploying into your AWS prod and preprod accounts: `PROD_AWS_ACCESS_KEY_ID`, `PROD_AWS_SECRET_ACCESS_KEY`, `PREPROD_AWS_ACCESS_KEY_ID`, and `PREPROD_AWS_SECRET_ACCESS_KEY`. If you use the same account for prod and preprod, just give the same values to the prod and preprod variables.
6. **(*)** Run the `CD storage` action. This creates the serverless Postgres. The database URL is printed in the Github console.
7. Run the `CD compute` action. This creates the serverless Spring Boot. The API URL is printed in the Github console.

**(*) Mandatory if you want POJA to fully manage Postgres: from creation, to operations -- scale-in, scale-out to zero, DDoS protection, regular backups -- to deletion. Optional if you want to do all of that manually yourself, typically if you already have an existing Postgres.**

## Use cases

### Create a completely new project with default options

```
pip install poja
python -m poja \
  --app-name=poja-base \
  --package-full-name=com.company.base \
  --region=eu-west-3 \
  --output-dir=folder-to-be-created
```

Those configurations will be automatically saved in `poja.yml` at the end of the creation.

### Upgrade an already existing project

```
pip install poja --upgrade
python -m poja \
  --app-name=poja-base \
  --package-full-name=com.company.base \
  --region=eu-west-3 \
  --output-dir=folder-already-created
```

Note the `--upgrade` and the `--output-dir=folder-already-created` flags.

The POJA configuration that was used for the previous generation is saved in `poja.yml`: it will be updated after the new upgrade.

### Use custom/additional Java deps

Just provide the argument `--custom-java-deps=your-list-of-deps`
where `your-list-of-deps` contains the dependency lines that are to be added to `build.gradle`.
[Here](./custom-java-deps-aws-ses.txt) is an example of such a file.

Once the generation finishes, `your-list-of-deps` will be copied at the root path of the genrated directory,
under the name `poja-custom-java-deps.txt`.
That file will come handy for future generations based on past generations.

### Use custom/additional Java env vars

Similar to the Java deps section above, but with `--custom-java-env-vars` as argument name.
[Here](./custom-java-env-vars.txt) is an example of such a file.

### Use your own VPC

Create first:
- Two subnets. They MUST be private, and access Internet through a NAT Gateway. Reference their id in SSM under any name you want.
- A security group that allows HTTP and Postgres traffic. Put its id in SSM under any name you want.

> **Warning**
> Remind that the NAT Gateway associated to the subnets is __not__ serverless.
> Whether your POJA is used or not, the NAT Gateway will generate a fixed lower cost of around $35 per month.
> If you host 100 POJA in the same VPC, that makes $0.35 the fixed cost per POJA.

Then invoke Poja CLI with the following additional parameters:
```
--with-own=vpc=true \
--ssm-sg-id=/poja/sg/id \
--ssm-subnet1-id=/poja/subnet/private1/id \
--ssm-subnet2-id=/poja/subnet/private2/id
```

### Do not create a new Postgres

Use `--with-postgres=false`. Handy if you want to use an already existing Postgres, that you will manually reference through custom Java env vars.



