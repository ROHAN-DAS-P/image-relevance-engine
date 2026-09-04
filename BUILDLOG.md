# BUILDLOG.md — AI Usage & Development Log

## 1. Purpose

This document records how AI tools were used during the development of the FlyRank AI Image Matching Engine.

AI was used primarily as a development assistant for debugging, code suggestions, architecture discussions, documentation, and reviewing implementation decisions. The generated suggestions were not treated as automatically correct. I tested, reviewed, modified, and verified the suggestions before using them in the project.

---

## 2. Where AI Helped

### Project Architecture

AI helped me reason about the overall backend architecture and break the project into separate components:

* FastAPI API layer
* PostgreSQL database
* pgvector for vector storage
* Gemini vision processing
* Gemini embeddings
* Semantic matching
* Mismatch Guard
* Background image-processing jobs
* Review/approval workflow
* Evaluation pipeline

This helped me structure the project into separate service modules instead of putting all processing logic inside the API endpoints.

---

### Database Design

AI helped with designing and reviewing the SQLAlchemy models for:

* Images
* Image metadata/tags
* Posts
* Matches
* AI cost logs

It also helped identify the need for:

* UUID identifiers
* Foreign keys
* Timestamps
* Vector columns
* Indexes
* Cascade behavior
* Uniqueness constraints

I reviewed the generated suggestions against the actual application requirements before implementing them.

---

### pgvector and Alembic

AI was particularly useful while setting up PostgreSQL and pgvector.

I encountered an error where the migration attempted to create a `VECTOR(768)` column before the PostgreSQL `vector` extension existed.

The migration was changed so that the extension is created before tables containing vector columns are created.

Example:

```python
op.execute("CREATE EXTENSION IF NOT EXISTS vector")
```

AI also helped explain the difference between SQLAlchemy's model definitions and Alembic migrations, and why `Base.metadata.create_all()` should not be relied on when Alembic is being used to manage the database schema.

---

### Vision Pipeline

AI helped me design the structured vision-response flow.

The vision model returns information such as:

* Objects
* Animal/category
* Colors
* Scene
* Confidence
* Description

The response is validated against a Pydantic schema before being used by the application.

This was important because a free-form LLM response should not be trusted directly by the matching system.

---

### Embeddings and Semantic Matching

AI helped me understand how image metadata and post text could be represented as embeddings and compared using cosine similarity.

The project uses:

* Gemini embeddings
* 768-dimensional vectors
* PostgreSQL/pgvector
* Cosine similarity

AI also helped me reason about semantic equivalence, such as:

> "red fox" ↔ "Vulpes vulpes"

rather than relying only on exact keyword matching.

---

### Mismatch Guard

AI helped brainstorm safety rules for preventing semantically similar but incorrect recommendations.

For example, a wolf image may have a reasonably high embedding similarity to a fox-related post because both are animals.

The Mismatch Guard was therefore added as a separate rule-based layer rather than trusting the similarity score alone.

This was tested using the wolf-on-fox scenario.

---

### API and Documentation

AI helped generate and refine:

* FastAPI endpoint structures
* Request/response schemas
* API documentation
* README sections
* Swagger documentation descriptions
* Curl examples
* Submission documentation

I still tested the endpoints using the running application and Swagger UI rather than assuming the generated code worked.

---

## 3. Where AI Was Wrong or Needed Correction

AI suggestions were not always correct.

### Incorrect Database Port Assumption

During PostgreSQL/Docker setup, there was a mismatch between the host port used by Docker and the port used in the application configuration.

Docker was configured with:

```text
5433:5432
```

but some connection attempts were made against the wrong port.

This resulted in a connection-refused error.

I corrected the database configuration so that the application uses the actual exposed host port.

---

### pgvector Migration Issue

An initial migration attempted to create a vector column before the PostgreSQL vector extension was available.

This produced an error similar to:

```text
psycopg2.errors.UndefinedObject:
type "vector" does not exist
```

The migration was corrected to explicitly enable the extension before creating the vector-dependent tables.

---

### Over-reliance on Similarity Scores

One important design lesson was that a high cosine similarity score does not necessarily mean that an image is a correct recommendation.

For example:

```text
fox ↔ wolf
```

can produce a relatively high semantic similarity because the concepts are related.

The system therefore needed additional mismatch rules instead of accepting the highest similarity score blindly.

---

### Evaluation Logic Required Review

AI-generated evaluation logic initially treated a suggested result as evidence of a correct result.

That is not the same as measuring true precision.

A proper precision calculation requires known expected labels/ground truth and comparison between the predicted result and the correct result.

This made me review the evaluation approach rather than accepting a seemingly valid percentage as proof of model accuracy.

---

### Documentation Can Overstate Completion

AI-generated documentation can sometimes make a feature sound complete simply because the corresponding code exists.

I learned that:

> Code existing ≠ feature being fully verified.

For example, a requirement should not be marked as complete merely because an endpoint or function exists. It should have a test, execution result, or other evidence demonstrating that it works.

This influenced how I prepared `EVIDENCE.md`.

---

## 4. What I Changed Myself

I did not directly accept all AI-generated code.

I personally:

* Ran the application locally.
* Debugged Docker/PostgreSQL connection issues.
* Ran Alembic migrations.
* Fixed database configuration problems.
* Verified pgvector setup.
* Tested API endpoints.
* Tested image-processing jobs.
* Checked matching behavior.
* Tested the mismatch scenario.
* Reviewed generated code for correctness.
* Adjusted configuration values.
* Modified database migrations.
* Reviewed evaluation logic.
* Prepared the final submission evidence.
* Verified that documentation matched the implemented project.

---

## 5. AI vs Human Responsibility

AI was used as an assistant rather than as an autonomous developer.

| Area          | AI Contribution              | My Responsibility                              |
| ------------- | ---------------------------- | ---------------------------------------------- |
| Architecture  | Suggestions and alternatives | Final architecture decisions                   |
| Database      | Schema suggestions           | Implementation and migration verification      |
| FastAPI       | Endpoint/code suggestions    | Integration and testing                        |
| Gemini        | API usage guidance           | Actual integration and validation              |
| Embeddings    | Matching approach            | Implementation and testing                     |
| Debugging     | Possible causes and fixes    | Running commands and confirming fixes          |
| Testing       | Test ideas/code suggestions  | Running and reviewing tests                    |
| Documentation | Drafting and formatting      | Final review and accuracy                      |
| Evaluation    | Metric/code suggestions      | Checking whether the metric was actually valid |

---

## 6. Key Lessons From Using AI

The biggest lesson was that AI is useful for accelerating development, but generated code still needs to be treated as a hypothesis.

The most useful workflow was:

```text
AI suggestion
     ↓
Implement
     ↓
Run locally
     ↓
Observe actual result
     ↓
Debug / modify
     ↓
Test again
     ↓
Keep only verified behavior
```

AI was especially useful for explaining unfamiliar errors and suggesting possible approaches. However, the actual application behavior was determined by running the code and verifying the results.

---

## 7. Final Reflection

AI significantly reduced the time required to research implementation approaches, debug errors, and prepare documentation.

At the same time, several AI suggestions required correction or additional verification. The experience showed me that using AI effectively is not about accepting generated code blindly. It is about understanding the suggestion, testing it against the real system, identifying incorrect assumptions, and making the final engineering decision myself.

The final implementation therefore combines AI-assisted development with manual debugging, testing, verification, and engineering judgment.
