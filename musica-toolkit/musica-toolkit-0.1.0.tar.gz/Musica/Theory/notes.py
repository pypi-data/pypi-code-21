        elif abs(alteration) == 1:
            temperament = self.__temperament__
            step_number = self._step_number
            true_step_number = temperament.fold_step_number(step_number + alteration)
            octave = self._octave
            if alteration < 0 and step_number == 0:
                octave -= 1
            elif alteration > 0 and temperament.is_last_step_number(step_number):
                octave += 1
            if alteration < 0:
                accidental = '#'
            else:
                accidental = '-'
            step = temperament[true_step_number].step
            print(step_number, alteration, true_step_number, step)
            return self.__class__(step=step, accidental=accidental, octave=octave)
