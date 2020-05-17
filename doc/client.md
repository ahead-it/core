# Client
The most advanced usage of Core is through client connected via websocket. Initialization is done via HTTP(s) and REST, after authentication transport is based on websocket for maximum performance and bidirectional messaging.

## Introduction
Following examples are based on `core-base` app, but Core allows implementation of any type of subsystem.

## Initialization
Client calls via HTTP(s) an initialization function that response with some constant string and the elements to construct a login page. Initialization function returns also authentication status (for example by a previous exchanged cookie) so the client can go directly to homepage skipping login.

RPC POST to `rpc/SessionManagement/initialize`
```json
{
}
```

RPC response
```json
{
  "background": "background.png",
  "logo": "logo.png",
  "name": "ACME Portal",
  "description": "User portal",
  "copyright": "2020 ACME Corporation",
  "authenticated": false,
  "startpage": "app.page.Welcome",
  "label_signin": "Sign in",
  "label_pwdlostqst": "Password lost?",
  "label_email": "E-Mail",
  "label_password": "Password",
  "label_pwdlost": "Password lost",
  "label_back": "Back",
  "label_send": "Send"
}
```

## Authentication
Authentication is made via RPC POST to `rpc/SessionManagement/login`
```json
{
  "email": "john@acme.com",
  "password": "mypassword",
}
```

RPC response (empty is successful or error)
```json
{
}
```

## Start page
Initialization method returns the name of the starting page that should be called after websocket opening.

Websocket Client > Server
```json
{
  "type": "invoke",
  "classname": "app.page.Welcome",
  "method": "run",
  "arguments": {}
}
```

Websocket Server > Client
```json
{
  "type": "response",
  "value": null
}
```

The `response` is the returning value of `run` function of `app.page.Welcome` page. For each `invoke` request there is a `response` response.

But in websocket client mode, more message will come from server when running a page.

Websocket Server > Client
```json
{
  "type": "send",
  "value": {
    "action": "page",    
    "id": "8912eecc-aea2-4c6f-a634-c21b87c77117",
    "name": "Welcome",
    "caption": "Welcome Page",
    "controls": [
      {
        "id": "1dd5277d-b7c5-4299-9089-77031e5eb7e5",
        "type": "AppCenter",
        "controls": [
          {
            "id": "735e5af1-f129-48fb-a76f-04596d058e24",
            "type": "ActionArea",
            "controls": [
              {
                "id": "8bc3841a-7d4b-43fe-880a-9c9467ae686f",
                "type": "Action",
                "controls": [],
                "caption": "Components"
              },
              {
                "id": "10fc6be8-91a1-4520-a43a-d4f0ea702fb8",
                "type": "Action",
                "controls": [],
                "caption": "Applications"
              },
              {
                "id": "a735178d-27fa-4625-b4ee-d88b6c6a495b",
                "type": "Action",
                "controls": [
                  {
                    "id": "e4e5272f-f005-44cc-9ef2-3c782a322fd3",
                    "type": "Action",
                    "controls": [
                      {
                        "id": "d46b0cef-8976-4af7-920d-0f405848eac8",
                        "type": "Action",
                        "controls": [],
                        "caption": "Error 1"
                      },
                      {
                        "id": "f2d6b0b8-f149-4826-9377-cd07b32683aa",
                        "type": "Action",
                        "controls": [],
                        "caption": "Error 2"
                      },
                      {
                        "id": "921ada34-2a40-4f30-8196-5da5d46cb82e",
                        "type": "Action",
                        "controls": [],
                        "caption": "Error 3"
                      }
                    ],
                    "caption": "Error Pages",
                    "icon": "fa-exclamation-triangle"
                  }
                ],
                "caption": "Custom"
              },
              {
                "id": "bc4a515d-6464-4732-8c93-76440383b5d3",
                "type": "Action",
                "controls": [],
                "caption": "Wizard",
                "icon": "fa-magic"
              }
            ]
          },
          {
            "id": "04621acf-88f1-48f4-a7d8-05282800fd5c",
            "type": "Search",
            "controls": []
          },
          {
            "id": "550dfcf1-c245-4a2b-a45f-e991f6b6de92",
            "type": "UserCenter",
            "controls": [
              {
                "id": "7993145e-4420-4523-9a7f-d34fd3801963",
                "type": "ActionList",
                "controls": [
                  {
                    "id": "e0593581-db88-4def-99ff-17e136701519",
                    "type": "Action",
                    "controls": [],
                    "caption": "My Profile",
                    "icon": "fa-user",
                    "description": "Account settings and more"
                  },
                  {
                    "id": "0996efb3-da26-4cf7-b45e-90d99ac5fdbb",
                    "type": "Action",
                    "controls": [],
                    "caption": "My Messages",
                    "icon": "fa-envelope-o",
                    "description": "Inbox and tasks"
                  }
                ]
              },
              {
                "id": "a8509467-4430-4aa8-8b9d-9f2449e5cac1",
                "type": "ActionArea",
                "controls": [
                  {
                    "id": "748f9ee6-8758-422b-b323-0cf88fe00c2c",
                    "type": "Action",
                    "controls": [],
                    "caption": "Sign out"
                  }
                ]
              }
            ]
          },
          {
            "id": "1232ed61-cfd6-4c41-a1dc-9cccce82a8d8",
            "type": "NavigationPane",
            "controls": [
              {
                "id": "c4395350-ad1f-41ff-9f82-2a54eacabd20",
                "type": "Action",
                "controls": [],
                "caption": "Dashboard",
                "icon": "fa-home"
              },
              {
                "id": "eff4e454-6014-4fde-8e64-e8eb68de6985",
                "type": "ActionGroup",
                "controls": [],
                "caption": "Applications"
              },
              {
                "id": "ea7749b2-bda0-4b72-8803-e2231a6b7f06",
                "type": "Action",
                "controls": [],
                "caption": "eCommerce",
                "icon": "fa-shopping-cart"
              },
              {
                "id": "19ef1ab3-2b2a-4f46-a5f3-96a31b924236",
                "type": "Action",
                "controls": [],
                "caption": "Customers"
              },
              {
                "id": "1085a789-7e41-460a-a616-cd9cbdca16d5",
                "type": "Action",
                "controls": [],
                "caption": "Products"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

Above JSON represents a request for a new page in the client.

## Messages
Not only `invoke` / `response` pair, other messages are handled.

`send` represents an action to be executed by the client without returning a value to the server (for example control refresh, popup message...)

Websocket Server > Client
```json
{
  "type": "send",
  "value": {
    "action": "message",
    "message": "Error 2 pressed",
    "title": null
  }
}
```

`sendrecv` represents an action that must return a value to the server. Until the answer is not sent, process execution on the server side is blocked.

Websocket Server > Client
```json
{
  "type": "sendrecv",
  "value": {
    "action": "confirm",
    "message": "Continue?",
    "default": false,
    "title": null
  }
}
```

Websocket Client > Server
```json
{
  "type": "answer",
  "value": false
}
```

### Message
It tells to the client to show a popup message.

```json
{
  "action": "message",
  "message": "Error 2 pressed",
  "title": null
}
```

### Confirm
It tells to the client to show a confirm message. The answer value is boolean.

```json
{
  "action": "confirm",
  "message": "Continue?",
  "default": false,
  "title": null
}
```
* `default` is the default button of the popup (Yes or No)

## Interact with controls
Each control is owned by a page. Page and control have their own ID.

For example, to invoke `click` method on a specific action:

Websocket Client > Server
```json
{
  "type": "invoke",
  "objectid": "f4dd13e4-d7d0-44f2-82db-3e442c5e8abd",
  "method": "_ctlinvoke",
  "arguments": {
    "method": "click",
    "controlid": "163085a9-793e-4055-8b31-2bd40515efde"
  }
}
```
* `_ctlinvoke` is a magic method of the page object that calls the requested function of the specified control.

## Dataset
Each page is bound to a dataset. Dataset comes from database tables.

```json
...
  "schema": [
    {
      "caption": "ID",
      "codename": "id",
      "type": "Code",
      "hasformat": false
    },
    {
      "caption": "Name",
      "codename": "name",
      "type": "Text",
      "hasformat": false
    },
    {
      "caption": "E-Mail",
      "codename": "email",
      "type": "Code",
      "hasformat": false
    },
    {
      "caption": "Enabled",
      "codename": "enabled",
      "type": "Boolean",
      "hasformat": true
    },
    {
      "caption": "Password",
      "codename": "password",
      "type": "Text",
      "hasformat": false
    },
    {
      "caption": "Last login",
      "codename": "lastlogin",
      "type": "DateTime",
      "hasformat": true
    }
  ]
...
```

`hasformat` property tells that the field data is available in "human readable"
value over than in raw value.
Each field control is bound to the dataset through `codename`.

```json
...
  {
    "id": "7a022b51-acd3-4f9c-9344-1359c4ec0c18",
    "type": "Field",
    "controls": [],
    "caption": "ID",
    "codename": "id",
    "controltype": "DEFAULT",
    "datatype": "CODE"
  },
  {
    "id": "6b81644a-cb97-49c6-b73e-14afb1c2666c",
    "type": "Field",
    "controls": [],
    "caption": "Name",
    "codename": "name",
    "controltype": "DEFAULT",
    "datatype": "TEXT"
  },
  {
    "id": "7ee4f035-098b-4de4-b7cc-d88e072ea585",
    "type": "Field",
    "controls": [],
    "caption": "E-Mail",
    "codename": "email",
    "controltype": "DEFAULT",
    "datatype": "TEXT"
  },
  {
    "id": "60af6880-ac7d-4e52-b1f9-02c80d1e4413",
    "type": "Field",
    "controls": [],
    "caption": "Password",
    "codename": "password",
    "controltype": "PASSWORD",
    "datatype": "TEXT"
  },
  {
    "id": "b71ee1ff-f94a-41d5-8a40-efffec0b5c3f",
    "type": "Field",
    "controls": [],
    "caption": "Enabled",
    "codename": "enabled",
    "controltype": "DEFAULT",
    "datatype": "BOOLEAN"
  }
...
```

Dataset returns raw values, formatted values and row count to allow
pagination. If the field does not support formatted value, empty string
is returned.

```json
{
  "dataset": [
    [
      "JOHN",
      "John Doe",
      "",
      false,
      "",
      "2020-05-18 00:58:44.900000+0200"
    ],
    [
      "BILL",
      "Bill Mayer",
      "",
      false,
      "",
      "2020-05-18 00:33:00.000000+0200"
    ]
  ],
  "fdataset": [
    [
      "",
      "",
      "",
      "No",
      "",
      "18/05/2020 00:58:44"
    ],
    [
      "",
      "",
      "",
      "No",
      "",
      "18/05/2020 00:33:00"
    ]
  ],
  "count": 1
}
```

After field validation the current dataset row is returned, so
a field can initialize several other related fields.

```json
{
  "datarow": [
    "JOHN",
    "John Doe",
    "john@contoso.com",
    false,
    "",
    null
  ],
  "fdatarow": [
    "",
    "",
    "",
    "No",
    "",
    ""
  ]
}
```

## Messages
Server can send several message to client:
* `disconnect` to close socket and restart
* `refreshpage` to reload page dataset
* `closepage` to close the page
* `changectlprop` to change page control property at runtime