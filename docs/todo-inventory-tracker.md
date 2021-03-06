### Features:
- [x] Decide name
- [x] get URL
- [x] fork &  
- [x] modify code to allow multiple users
- [ ] orgs/users
- [ ] authorization
- [ ] deploy with uwsgi
- [ ] get new stickers printed
- [ ] add editing
- [ ] add location via GPS for input
- [ ] gmaps integration showing location of objects

### Bugs:
- [ ] Image upload doesn't work

openlogistix.io

url scheme:
```
 _________________________________________________________________________________________
| Function            | URL                                                               |
|---------------------+-------------------------------------------------------------------|
| org admin           | https://openlogistix.io/org/<int:org_id>/                         |
| list inventory      | https://openlogistix.io/org/<int:org_id>/inventory/               |
| create/display/edit | https://openlogistix.io/org/<int:org_id>/inventory/<int:obj_id>   |
```
table schemes:

"item" table
```
                            Table "public.item"
   Column    |  Type   |                     Modifiers
-------------+---------+---------------------------------------------------
 id          | integer | not null default nextval('item_id_seq'::regclass)
 org_id      | integer |
 qr_id       | integer |
 name        | text    |
 imagepath   | text    |
 location    | text    |
 tags        | json    |
 description | text    |

"org" table
                           Table "public.org"
  Column   |  Type   |                    Modifiers
-----------+---------+--------------------------------------------------
 id        | integer | not null default nextval('org_id_seq'::regclass)
 name      | text    |
 itemlimit | integer |
Indexes:
    "org_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "item" CONSTRAINT "org_constraint" FOREIGN KEY (org_id) REFERENCES org(id)
```
