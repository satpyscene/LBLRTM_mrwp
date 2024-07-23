import lblrtm_tape11_reader

import matplotlib
# matplotlib.use('Agg')

 
import matplotlib.pyplot as plt
v,rad=lblrtm_tape11_reader.lblrtm_tape11_reader1('ODint_001-13500.000','s')
# v=v[:-1]
plt.plot(v,rad)
plt.show()
plt.savefig('test.png')
