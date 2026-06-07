---
name: api-patterns
description: "Design APIs, choose between REST/GraphQL/tRPC, review API architecture. Use whenever the user mentions API design, endpoint, route, REST, GraphQL, tRPC, HTTP, webhook, OpenAPI, Swagger, API versioning, or wants to create, review, or refactor any API surface. Trigger even if the user doesn't explicitly say 'API' — any discussion of endpoints, routes, or data contracts should use this."
license: MIT
allowed-tools: "Read, Grep, Glob"
---

# API Design Patterns

## Decision Tree: REST vs GraphQL vs tRPC

**REST** — Use when:
- Public API consumed by unknown clients
- Needs caching and CDN support
- Simple CRUD operations
- Multiple client types (web, mobile, third-party)

**GraphQL** — Use when:
- Complex data requirements with nested queries
- Mobile clients with bandwidth concerns
- Multiple teams need flexible queries
- Client-driven data fetching

**tRPC** — Use when:
- TypeScript monorepo (shared types)
- Full-stack TypeScript project
- Internal API with same-language consumers
- Maximum type safety needed

## API Design Checklist

- [ ] Chosen API style based on THIS context (not defaulting)
- [ ] Consistent response format defined (envelope pattern)
- [ ] HTTP methods used correctly (GET read, POST create, PUT replace, PATCH update, DELETE remove)
- [ ] Meaningful status codes (200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Server Error)
- [ ] Versioning strategy planned (URI `/v1/`, Header `Accept-Version`)
- [ ] Authentication and authorization defined
- [ ] Rate limiting planned
- [ ] Documentation approach (OpenAPI/Swagger)

## Anti-Patterns

- Defaulting to REST for everything without analysis
- Using verbs in REST endpoints (`/getUsers`, `/createOrder`)
- Returning inconsistent response formats across endpoints
- Exposing internal errors to clients (stack traces, database errors)
- Skipping rate limiting on public endpoints
- Mixing API styles arbitrarily in one project

## Response Format (Envelope Pattern)

```json
{
  "data": {
    /* payload */
  },
  "error": null,
  "meta": { "page": 1, "total": 42 }
}
```

Errors: `{ "data": null, "error": { "code": "VALIDATION_ERROR", "message": "..." }, "meta": null }`
