create table snippets (
keyword text primary key,
message text not null default '',
hidden_status bool not null default false
);