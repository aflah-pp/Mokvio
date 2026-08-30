import DocLayout from "@/features/docs/components/layout/doc-layout";
import MarkdownRenderer from "@/features/docs/components/markdown/md-rendorer";
import DocsPagination from "@/features/docs/components/navigation/doc-pagination";

const content = `
# Introduction

Welcome to **Mokvio**.

Mokvio is a simple mock API generator for developers who need an API while building an application.

Instead of waiting for a real backend, you can create a project, define your API resources and fields, configure how data should be generated, and start making HTTP requests immediately.

## What can you do with Mokvio?

With Mokvio you can:

- Create projects
- Create API resources
- Add fields to resources
- Choose field types
- Configure data generators
- Publish resources
- Generate mock API endpoints
- Send HTTP requests to your APIs
- Test common API operations
- Use the APIs from any application or HTTP client

The basic workflow is:

\`\`\`text
Create Project
      ↓
Create Resource
      ↓
Add Fields
      ↓
Configure Generators
      ↓
Publish
      ↓
Get API URL
      ↓
Make HTTP Requests
\`\`\`

## Why use Mokvio?

Imagine you are building a frontend and need:

\`\`\`text
GET /products
\`\`\`

But your real backend is not ready yet.

Instead of waiting for the backend, create the API structure in Mokvio and use it immediately.

Your development workflow becomes:

\`\`\`text
Frontend
   ↓
Mokvio Mock API
   ↓
JSON Response
\`\`\`

This lets you build:

- Pages
- Tables
- Forms
- Loading states
- Empty states
- Error handling
- API integrations
- Mobile application screens

before the production backend is available.

## Core concepts

Mokvio is built around three main concepts.

### Project

A project groups related API resources.

For example:

\`\`\`text
Ecommerce
├── Product
├── User
├── Order
└── Category
\`\`\`

### Resource

A resource represents a type of data exposed by your mock API.

Examples:

\`\`\`text
Product
User
Order
Category
\`\`\`

A resource contains the fields that define its data structure.

### Field

A field represents a piece of data inside a resource.

For example:

\`\`\`text
Product
├── name
├── price
├── stock
└── image
\`\`\`

Each field has a type and can use a generator to produce mock data.

## Data generators

Generators determine what kind of value Mokvio produces for a field.

For example:

\`\`\`text
name
 ↓
Full Name
 ↓
"John Smith"
\`\`\`

Another field might use:

\`\`\`text
price
 ↓
Price Generator
 ↓
2499.99
\`\`\`

Generators allow you to create more realistic API responses without manually entering large amounts of fake data.

## Generated data

Mokvio stores your API structure and generation configuration.

It does not require you to manually create hundreds of fake records.

When your mock API is requested, Mokvio generates data from the resource and field configuration.

For example:

\`\`\`text
Resource
   ↓
Field Configuration
   ↓
Generator
   ↓
Generated JSON
\`\`\`

The generated values can change between requests depending on the generator being used.

## HTTP methods

Mokvio supports common HTTP operations for working with your mock APIs.

These can include:

\`\`\`text
GET
POST
PUT
PATCH
DELETE
\`\`\`

You can use these methods to test common frontend API workflows such as:

- Reading data
- Creating data
- Updating data
- Partially updating data
- Deleting data

The exact behavior depends on the current resource and API implementation.

## Example API

A Product resource might contain:

\`\`\`text
Product
├── name
├── price
├── stock
└── image
\`\`\`

After publishing the resource, Mokvio provides an API endpoint.

You can then request it from:

- JavaScript
- React
- Vue
- Angular
- React Native
- Flutter
- Postman
- Axios
- Fetch
- Any HTTP client

## What Mokvio is for

Mokvio is useful for:

- Frontend development
- API prototyping
- UI development
- API integration testing
- Demo applications
- Hackathons
- Mobile application development
- Testing API-driven interfaces

## What Mokvio is not

Mokvio is designed for development and testing.

It is not intended to replace a production backend.

Your production application may still require:

- Application-specific business logic
- Permanent data storage
- Complex relationships
- Payments
- Production authorization
- Custom backend workflows

Mokvio gives you a fast API environment while you build and test your application.

## Next step

Continue with **Quick Start** to create your first mock API.
`;

function Introduction() {
  return (
    <DocLayout>
      <div className="mx-auto w-full max-w-4xl px-6 py-10">
        <MarkdownRenderer>{content}</MarkdownRenderer>

        <DocsPagination />
      </div>
    </DocLayout>
  );
}

export default Introduction;
