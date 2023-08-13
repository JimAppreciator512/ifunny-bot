create table if not exists "Config" (
    server varchar(40) primary key not null,
    globalEmbed boolean not null default true,
    role varchar(19) not null default ""
);

create table if not exists "Channel" (
    channel varchar(19) primary key not null,
    server varchar(40) not null,
    foreign key (server) references Config(server),
    unique(channel)
);

