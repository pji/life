"""
__main__
~~~~~~~~

Mainline for :mod:`life`.
"""
import traceback as tb

from life.main import main


try:
    main()
except Exception as ex:
    with open('exception.log', 'a') as fh:
        fh.write(str(type(ex)) + '\n')
        fh.write(str(ex.args) + '\n')
        tb_str = ''.join(tb.format_tb(ex.__traceback__))
        fh.write(tb_str)
    raise ex
