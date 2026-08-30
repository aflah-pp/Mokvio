import DocLayout from "@/features/docs/components/layout/doc-layout";
import MarkdownRenderer from "@/features/docs/components/markdown/md-rendorer";
import DocsPagination from "@/features/docs/components/navigation/doc-pagination";

const content = `
# Quick Start

Let's create a simple **Product API** with Mokvio.

You do not need to build a backend or create a database table.

## 1. Create a project

Open the Mokvio dashboard.

Create a new project.

For example:

\`\`\`text
Ecommerce
\`\`\`

A project is used to organize your API resources.

## 2. Create a resource

Open your project and create a resource named:

\`\`\`text
Product
\`\`\`

Your project now looks like:

\`\`\`text
Ecommerce
└── Product
\`\`\`

A resource represents the data provided by your mock API.

## 3. Add fields

Open the Product resource and add fields.

For example:

| Field | Type | Generator |
| --- | --- | --- |
| name | String | Full Name |
| price | Decimal | Price |
| stock | Integer | Integer |
| image | String | Image URL |
| active | Boolean | Boolean |

Each field defines one piece of data in the API response.

## 4. Configure generators

Choose a generator for each field.

For example:

\`\`\`text
name
 ↓
Full Name
 ↓
"John Smith"

price
 ↓
Price
 ↓
2499.99

stock
 ↓
Integer
 ↓
42

active
 ↓
Boolean
 ↓
true
\`\`\`

Generators allow Mokvio to create realistic mock values automatically.

## 5. Publish the resource

When your resource and fields are ready, publish the resource.

Publishing makes the resource available through the mock API.

## 6. Get your API URL

Open the API or runtime section of your resource.

Mokvio will provide your generated API URL.

It will look similar to:

\`\`\`text
https://your-mokvio-url/api/ecommerce/product
\`\`\`

Your actual URL depends on your project and resource.

## 7. Make a GET request

Open the API URL in your browser or use Postman.

A GET request returns generated JSON data.

For example:

\`\`\`json
{
  "name": "John Smith",
  "price": 2499.99,
  "stock": 42,
  "image": "https://example.com/image.jpg",
  "active": true
}
\`\`\`

The generated values can change between requests.

## 8. Make a POST request

If POST is supported by the resource, you can send JSON data to the API.

For example:

\`\`\`text
POST /api/ecommerce/product
\`\`\`

With a request body:

\`\`\`json
{
  "name": "Laptop",
  "price": 899.99,
  "stock": 20,
  "active": true
}
\`\`\`

This allows you to test frontend create operations.

## 9. Make a PUT request

PUT can be used to test update operations.

For example:

\`\`\`text
PUT /api/ecommerce/product/{id}
\`\`\`

Send the updated resource data in the request body.

## 10. Make a PATCH request

PATCH can be used to test partial updates.

For example:

\`\`\`text
PATCH /api/ecommerce/product/{id}
\`\`\`

You can send only the fields that need to be changed.

For example:

\`\`\`json
{
  "stock": 15
}
\`\`\`

## 11. Make a DELETE request

DELETE can be used to test deletion workflows.

For example:

\`\`\`text
DELETE /api/ecommerce/product/{id}
\`\`\`

This is useful when testing frontend delete actions.

## 12. Use the API in your application

Once you have your API URL, you can use it from any application.

For example:

\`\`\`javascript
const response = await fetch(
  "https://your-mokvio-url/api/ecommerce/product"
);

const data = await response.json();
\`\`\`

You can also use Axios, React Query, Fetch, Postman, or another HTTP client.

## Complete workflow

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
Copy API URL
      ↓
GET / POST / PUT / PATCH / DELETE
      ↓
Use API in Your Application
\`\`\`

## Example frontend workflow

You can develop your frontend against Mokvio while your real backend is still being built.

For example:

\`\`\`text
Frontend
   ↓
Mokvio
   ↓
Mock JSON
\`\`\`

Later, when your production backend is ready:

\`\`\`text
Frontend
   ↓
Production API
   ↓
Real Backend
\`\`\`

Your frontend can be developed independently from the backend.

## What's next?

You now know the complete Mokvio workflow:

- Create a project
- Create a resource
- Add fields
- Configure generators
- Publish the resource
- Get the API URL
- Make HTTP requests
- Connect the API to your application

Continue to **Installation** if you want to run Mokvio yourself.
`;

function QuickStart() {
  return (
    <DocLayout>
      <div className="mx-auto w-full max-w-4xl px-6 py-10">
        <MarkdownRenderer>{content}</MarkdownRenderer>

        <DocsPagination />
      </div>
    </DocLayout>
  );
}

export default QuickStart;
