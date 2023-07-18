create table if not exists "Config" (
    server varchar(18) primary key not null,
    globalEmbed boolean not null default true
);

create table if not exists "Channel" (
    server varchar(18) primary key not null,
    channel varchar(19) not null,
    foreign key (server) references Config(server),
    unique(channel)
);

