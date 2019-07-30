from celery.contrib.abortable import AbortableTask

class LRT(AbortableTask):

    def run(self):
        is_abt = False
        while not is_abt:
            is_abt = self.is_aborted(**kwargs)
            print("not aborted")
        print("aborted")

