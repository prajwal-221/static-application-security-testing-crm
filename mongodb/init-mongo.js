db = db.getSiblingDB('admin');


db = db.getSiblingDB('idurar');

db.createUser({
  user: 'idurar',
  pwd: 'idurar123',
  roles: [
    {
      role: 'readWrite',
      db: 'idurar',
    },
  ],
});
