# BNU Software Engineering

This repo contains the code used for our Software Engineering module.

It is assumed you are using Linux (including WSL2), and already have docker/docker-compose setup.

## Development

This project consists of 2 main parts: the frontend, and the services.

### Services

#### Running

The services can be run for development with the docker-compose.yml file, and any changes made to the service will automatically update
within the running container (as a volume is mounted). Changes to any dependencies will require rebuilding the containers.

Start services:
```
$ docker compose up --build
```

Rebuild containers:
```
$ docker compose down
$ docker compose up --build
```

#### Contributing

To add a service, use the users service as a baseline - including its requirements.txt. The Dockerfile shouldn't need any modification, 
but make sure to add the service to the docker-compose files (both production and normal).

`auth.py` should be copied to any new services, and endpoints should include `user = Depends(verify_user)` as a parameter. You don't need
to use this parameter, but adding it ensures that endpoints have the correct authentication (and a not logged in user cannot call them).

### Frontend

The frontend is built with **Vite + React** and uses React Router for navigation.

#### Running

During development, its easiest to just run the frontend directly:

```
$ cd frontend
$ npm ci # install dependencies from lock file
$ npm run dev
```

The app will be available at `http://localhost:3000`.

#### Environment Variables

Copy `.env.example` to `.env` and configure the service URLs:

```
VITE_USERS_SERVICE_URL=http://localhost:8001
VITE_APPLIANCES_SERVICE_URL=http://localhost:8002
VITE_FIRE_SAFETY_SERVICE_URL=http://localhost:8003
```

#### Contributing

We are using [shadcn](https://ui.shadcn.com/) for our components, and tailwind for extra styling. Both should be very easy to
pick up if you haven't used them before. One caviat with shadcn is components need to be added to a project before they can be
used. If you get an import error trying to use a component - it just needs to be installed, e.g: `npx shadcn@latest add card`.
Details can be found on each components page.

Adding a new service to our API requires adding a client in `lib/api/client.ts`, and defining the API in its own service file
(see `lib/api/users.ts`) for an example. Defining the API like this, rather than just using `axios(URL)...` ensures type safety,
and allows us to automatically add the auth token to requests when the user is logged in.

## Production

Running a 'production' instance requires you to create .env.production files in both `services/` and `frontend/` (examples are
in each directory already), and running:

```
$ docker compose -f docker-compose-prod.yaml up --build
```

This will start the entire project, with it accessible at `http://localhost:8080`. The frontend is built as a static site
and served via nginx. As this is a production build, there is no live editing supported here - changes will require rebuilding the project.
