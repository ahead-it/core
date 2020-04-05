# System Objects

## Session Management
Special codeunit `app.codeunit.SessionManagement` is searched by engine.
* `start` method is called when a session starts
* `stop` method is called when a session ends

This hook can be used to intialize session variables and store it on the database.