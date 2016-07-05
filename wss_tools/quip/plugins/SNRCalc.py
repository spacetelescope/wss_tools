"""SNR and Surface background ratio (SBR) calculation local plugin for QUIP."""
from __future__ import absolute_import, division, print_function

# STGINGA
from stginga.plugins.SNRCalc import SNRCalc as SNRCalcParent

# LOCAL
from wss_tools.quip.main import QUIP_DIRECTIVE

__all__ = []


class SNRCalc(SNRCalcParent):
    """SNR and SBR calculation on an image."""
    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(SNRCalc, self).__init__(fv, fitsimage)

        if QUIP_DIRECTIVE is None:
            self.op_type = ''
        else:
            self.op_type = QUIP_DIRECTIVE['OPERATION_TYPE'].upper()

    def set_minsbr(self):
        """Set SBR limit using the given key."""
        if self.op_type == 'MIMF':
            # ---- Extract header ----
            image = self.fitsimage.get_image()
            if image is None:
                intrume = ''
            else:
                imhdr = image.get_header()
                instrume = imhdr.get(self._ins_key, '').upper()

            if instrume in ('NIRCAM', 'NIRISS'):
                val = 1500
            elif instrume in ('NIRSPEC', 'MIRI', 'FGS'):
                val = 750
            else:
                val = 0

        elif self.op_type in ('FINE_PHASING', 'WAVEFRONT_MAINTENANCE'):
            val = 1500

        elif self.op_type in ('THUMBNAIL', 'FOCUS_SWEEP', 'SEGMENT_ID',
                         'SEGMENT_SEARCH', 'IMAGE_ARRAY', 'GLOBAL_ALIGNMENT',
                         'FVA_COARSE_MIMF', 'IMAGE_STACKING',
                         'FVA_FIELD_VIGNETTING_SCAN'):
            val = 500

        elif self.op_type == 'COARSE_PHASING':
            val = 30

        elif self.op_type == 'PUPIL_IMAGING':
            val = 25

        else:
            val = 0

        self.w.min_sbr.set_text(str(val))
        return val
