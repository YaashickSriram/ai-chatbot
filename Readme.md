## 3. Data Flow Diagram
```
User Query: "Compare Q1 vs Q2 satisfaction scores"
    │
    ▼
FastAPI Endpoint (/chat/query)
    │
    ▼
ReAct Agent (reasoning_node)
    │
    ├─► Azure OpenAI (gpt-4o)
    │       "Which tool should I use?"
    │       → Analyzes query
    │       → Returns: compare_data tool
    │
    ▼
ReAct Agent (action_node)
    │
    ├─► ComparisonTool.execute()
    │       │
    │       ├─► DataFrameManager.get_dataframe()
    │       │       │
    │       │       └─► Returns cached DataFrame
    │       │
    │       ├─► Execute pandas query:
    │       │   df.groupby('quarter')['satisfaction'].mean()
    │       │
    │       └─► Returns: {Q1: 7.5, Q2: 8.2}
    │
    ▼
ReAct Agent (response_node)
    │
    ├─► Azure OpenAI (gpt-4o)
    │       "Convert data to natural language"
    │       → Input: {Q1: 7.5, Q2: 8.2}
    │       → Output: "The satisfaction scores show an 
    │         improvement from Q1 to Q2, with Q1 averaging 
    │         7.5 and Q2 averaging 8.2, representing a 
    │         9.3% increase."
    │
    ▼
FastAPI Response
    │
    ▼
User receives natural language answer

--------------------------------------------------------------------------------------------------------------
Application Startup Sequence
--------------------------------------------------------------------------------------------------------------
┌─────┐          ┌─────────┐         ┌───────────┐        ┌──────────┐
│FastAPI│        │Snowflake│         │DataFrame  │        │ReAct     │
│ App   │        │Connector│         │Manager    │        │Agent     │
└───┬───┘        └────┬────┘         └─────┬─────┘        └────┬─────┘
    │                 │                    │                   │
    │ startup()       │                    │                   │
    ├────────────────►│                    │                   │
    │                 │                    │                   │
    │                 │ connect()          │                   │
    │                 ├───────────────────►│                   │
    │                 │                    │                   │
    │                 │ fetch_data()       │                   │
    │                 │◄───────────────────┤                   │
    │                 │                    │                   │
    │                 │   return DataFrame │                   │
    │                 ├───────────────────►│                   │
    │                 │                    │                   │
    │                 │                    │ store in memory   │
    │                 │                    ├──────────┐        │
    │                 │                    │          │        │
    │                 │                    │◄─────────┘        │
    │                 │                    │                   │
    │  initialize_agent()                  │                   │
    ├──────────────────────────────────────────────────────────►│
    │                 │                    │                   │
    │                 │                    │  create tools     │
    │                 │                    │◄──────────────────┤
    │                 │                    │                   │
    │   ready         │                    │                   │
    │◄────────────────────────────────────────────────────────┤
    │                 │                    │                   │

--------------------------------------------------------------------------------------------------------------
Query Processing Sequence
--------------------------------------------------------------------------------------------------------------    

    ┌────┐   ┌───────┐   ┌──────┐   ┌─────────┐   ┌────┐   ┌──────────┐
│User│   │FastAPI│   │ReAct │   │Azure    │   │Tool│   │DataFrame │
│    │   │       │   │Agent │   │OpenAI   │   │    │   │Manager   │
└─┬──┘   └───┬───┘   └───┬──┘   └────┬────┘   └─┬──┘   └────┬─────┘
  │          │           │           │          │           │
  │ POST     │           │           │          │           │
  │ /query   │           │           │          │           │
  ├─────────►│           │           │          │           │
  │          │           │           │          │           │
  │          │ run(query)│           │          │           │
  │          ├──────────►│           │          │           │
  │          │           │           │          │           │
  │          │           │ REASONING │          │           │
  │          │           │           │          │           │
  │          │           │ chat()    │          │           │
  │          │           ├──────────►│          │           │
  │          │           │           │          │           │
  │          │           │  tool_call│          │           │
  │          │           │◄──────────┤          │           │
  │          │           │           │          │           │
  │          │           │   ACTION  │          │           │
  │          │           │           │          │           │
  │          │           │ execute() │          │           │
  │          │           ├──────────────────────►│           │
  │          │           │           │          │           │
  │          │           │           │          │get_df()   │
  │          │           │           │          ├──────────►│
  │          │           │           │          │           │
  │          │           │           │          │ DataFrame │
  │          │           │           │          │◄──────────┤
  │          │           │           │          │           │
  │          │           │           │          │pandas ops │
  │          │           │           │          ├──────┐    │
  │          │           │           │          │      │    │
  │          │           │           │          │◄─────┘    │
  │          │           │           │          │           │
  │          │           │  result   │          │           │
  │          │           │◄──────────────────────┤           │
  │          │           │           │          │           │
  │          │           │  RESPONSE │          │           │
  │          │           │           │          │           │
  │          │           │ format()  │          │           │
  │          │           ├──────────►│          │           │
  │          │           │           │          │           │
  │          │           │ verbiage  │          │           │
  │          │           │◄──────────┤          │           │
  │          │           │           │          │           │
  │          │  response │           │          │           │
  │          │◄──────────┤           │          │           │
  │          │           │           │          │           │
  │  JSON    │           │           │          │           │
  │◄─────────┤           │           │          │           │
  │          │           │           │          │           │