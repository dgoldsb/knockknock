import datetime

import models

# POST
test = models.Sighting(datetime.datetime.now(), 'test')
models.session.add(test)
models.session.commit()

# GET
instance = models.session.query(models.Sighting).first()
print(instance.id)

print('Test done')
