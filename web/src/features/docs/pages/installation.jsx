import DocLayout from "@/features/docs/components/layout/doc-layout";
import MarkdownRenderer from "@/features/docs/components/markdown/md-rendorer";
import DocsPagination from "@/features/docs/components/navigation/doc-pagination";

const content = `
# Installation

Mokvio can be used in two ways:

1. **Hosted Mokvio**
2. **Self-hosted Mokvio**

## Hosted Mokvio

If you are using the hosted version of Mokvio, you do not need to install anything.

You only need a browser.

\`\`\`text
Browser
   ↓
Mokvio
   ↓
Create Mock API
   ↓
Use API in Your Application
\`\`\`

Open Mokvio, create your project, and start creating your mock API.

You do not need to install:

- Python
- Node.js
- PostgreSQL
- Django
- React

## Self-hosted Mokvio

If you want to run Mokvio on your own machine, you can clone the project and run the frontend and backend locally.

### Requirements

You need:

- Git
- Python 3.12+
- Node.js 20+
- npm
- PostgreSQL

You do not need to know Django or React to use Mokvio.

These are the technologies used to build the platform.

## 1. Clone Mokvio

Clone the repository:

\`\`\`bash
git clone <repository-url>
cd Mokvio
\`\`\`

The project contains two main parts:

\`\`\`text
Mokvio
├── server
└── web
\`\`\`

The \`server\` directory contains the backend.

The \`web\` directory contains the frontend.

## 2. Set up the backend

Open a terminal and go to the server:

\`\`\`bash
cd server
\`\`\`

Create a Python virtual environment:

\`\`\`bash
python -m venv .venv
\`\`\`

Activate it.

### macOS / Linux

\`\`\`bash
source .venv/bin/activate
\`\`\`

### Windows

\`\`\`powershell
.venv\\\\Scripts\\\\activate
\`\`\`

## 3. Install backend packages

Install the required packages:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 4. Configure the backend

Mokvio uses environment variables for its configuration.

Set up your local environment according to the project's environment configuration.

Typical values include:

\`\`\`text
SECRET_KEY
DATABASE_URL
CORS_ALLOWED_ORIGINS
\`\`\`

For PostgreSQL, the database URL will look similar to:

\`\`\`text
DATABASE_URL=postgresql://username:password@localhost:5432/mokvio
\`\`\`

Use your own PostgreSQL username, password, host, port, and database name.

Do not commit environment files or secrets to Git.

## 5. Create the PostgreSQL database

Create a PostgreSQL database for Mokvio.

For example:

\`\`\`text
mokvio
\`\`\`

Then configure \`DATABASE_URL\` to point to that database.

Mokvio stores API configuration such as:

- Projects
- Resources
- Fields
- Generator configuration

Generated mock data is produced when the API is requested.

## 6. Run database migrations

From the \`server\` directory:

\`\`\`bash
python manage.py migrate
\`\`\`

This creates the required database tables.

## 7. Start the backend

Run:

\`\`\`bash
python manage.py runserver
\`\`\`

The backend will normally be available at:

\`\`\`text
http://127.0.0.1:8000
\`\`\`

Keep this terminal running.

## 8. Start the frontend

Open another terminal.

From the Mokvio project directory:

\`\`\`bash
cd web
\`\`\`

Install the frontend packages:

\`\`\`bash
npm install
\`\`\`

Start the development server:

\`\`\`bash
npm run dev
\`\`\`

Vite will show the frontend address in your terminal.

It will normally look similar to:

\`\`\`text
http://localhost:5173
\`\`\`

Open that address in your browser.

## 9. Check that everything works

Once the frontend and backend are running:

1. Open Mokvio.
2. Create a project.
3. Create a resource.
4. Add fields.
5. Configure generators.
6. Publish the resource.
7. Open the generated API URL.
8. Make an HTTP request.
9. Verify that the API returns JSON.

If the API responds correctly, your local Mokvio installation is working.

## Hosted vs Self-hosted

### Hosted

Hosted Mokvio requires no local setup.

\`\`\`text
Browser
   ↓
Mokvio
\`\`\`

### Self-hosted

Self-hosted Mokvio runs on infrastructure you control.

\`\`\`text
Browser
   ↓
Mokvio Frontend
   ↓
Mokvio Backend
   ↓
PostgreSQL
\`\`\`

You are responsible for running and maintaining these services.

## Docker

Docker support is not available in the current version of Mokvio.

The current self-hosted setup uses:

- Python
- Node.js
- PostgreSQL

## Do I need a Mokvio package?

No.

Mokvio does not require an npm package or SDK.

Once you have a mock API URL, use it like any other HTTP API.

You can use:

- Fetch
- Axios
- React Query
- Postman
- Any HTTP client

## Final workflow

Once Mokvio is installed, the complete workflow is:

\`\`\`text
Project
   ↓
Resource
   ↓
Fields
   ↓
Generators
   ↓
Publish
   ↓
Mock API
   ↓
HTTP Requests
   ↓
Frontend / Mobile Application
\`\`\`

## Next step

Continue with **Quick Start** to create your first mock API.
`;

function Installation() {
  return (
    <DocLayout>
      <div className="mx-auto w-full max-w-4xl px-6 py-10">
        <MarkdownRenderer>{content}</MarkdownRenderer>

        <DocsPagination />
      </div>
    </DocLayout>
  );
}

export default Installation;
