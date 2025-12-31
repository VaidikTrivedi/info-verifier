``` mermaid
graph TD
    User[User API Request] -->|POST /verify| API[FastAPI Backend]
    API -->|Push Job| Redis[(Redis Queue)]
    API -->|Return JobID| User
    
    subgraph "Worker Nodes (Celery)"
        Redis -->|Pop Job| Worker[AI Worker]
        
        subgraph "LangGraph Tribunal"
            Start --> Decomposer
            Decomposer -->|List of Claims| Investigator
            Investigator -->|Search Results| Verifier
            Verifier -->|Contradictions?| RetryLoop{Needs More Info?}
            RetryLoop -->|Yes| Investigator
            RetryLoop -->|No| Judge
        end
        
        Worker -->|Save Report| DB[(Postgres/JSON)]
    end
    
    %% User -->|GET /status/{id}| API
    %% API -->|Fetch Report| DB
```