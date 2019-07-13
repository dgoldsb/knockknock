import datetime
import time

time.sleep(5)


import models

test = models.Sighting(datetime.datetime.now(), 'test')
models.session.add(test)
models.session.commit()
print('Test done')
