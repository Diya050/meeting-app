# Meeting Minutes Sending Flowchart

```mermaid
graph TD
  A[Start] --> B{Meeting Status == "Invitation Sent"}
  B -->|Yes| C[Check if Meeting Minutes Exist]
  C -->|Yes| D[Loop through Minutes]
  D --> E[Generate Email]
  E --> F[Send Email]
  F --> G{All Minutes Processed?}
  G -->|No| D
  G -->|Yes| H[Update Meeting Status]
  H --> I[Display Success Message]
  C -->|No| J[Display Error: No Minutes]
  B -->|No| K[Display Error: Wrong Status]
