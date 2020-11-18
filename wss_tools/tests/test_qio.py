import glob
import os

from astropy.utils.data import get_pkg_data_filename

from wss_tools.quip import qio


def test_opfile_validation():
    filename = get_pkg_data_filename('data/operation_file_001.xml')
    returncode, _, _ = qio.validate_input_xml(filename)
    assert returncode == 0


def test_validate_output_out_xml():
    filename = get_pkg_data_filename('data/quip_out_001.xml')
    returncode, _, _ = qio.validate_output_out_xml(filename)
    assert returncode == 0


def test_validate_output_log_xml():
    filename = get_pkg_data_filename('data/quip_activity_log_001.xml')
    returncode, _, _ = qio.validate_output_log_xml(filename)
    assert returncode == 0


def test_opfile_gen(tmpdir):
    """Test QUIP Operation File generator."""
    optype = 'MIMF'
    outdir = '/dummy/path'
    imname = 'dummy.fits'
    dummy_fits = tmpdir.join(imname)  # noqa
    dummy_fits.write('content')
    opfilename = os.path.join(tmpdir.strpath, 'operation_file_001.xml')
    opfile = qio.QUIPOpFile(optype, outdir, create_outdir=False)
    opfile.input_files = list(map(os.path.abspath, glob.iglob(
        os.path.join(tmpdir.strpath, '*.fits'))))

    assert len(opfile.input_files) == 1
    assert opfile.input_files[0].endswith(imname)

    opfile.write_xml(opfilename)

    # Make sure it round-trips and check the important stuff
    qio.validate_input_xml(opfilename)
    opdict = qio.input_xml(opfilename)
    imlist = opdict['IMAGES']['IMAGE_PATH']
    assert len(imlist) == 1
    assert imlist[0].endswith(imname)
    assert opdict['OPERATION_TYPE'] == optype
    assert opdict['OUTPUT']['OUTPUT_DIRECTORY'] == outdir
    assert (opdict['OUTPUT']['LOG_FILE_PATH'] ==
            os.path.join(outdir, 'R2017061401_quip_activity_log.xml'))
    assert (opdict['OUTPUT']['OUT_FILE_PATH'] ==
            os.path.join(outdir, 'R2017061401_quip_out.xml'))
    assert opdict['@creator'] == 'QUIP'


def test_get_quip_info():
    quip_info = qio._get_quip_info()
    assert quip_info['@creator'] == 'QUIP'
    assert quip_info['@operational'] == 'false'
    assert isinstance(quip_info['@version'], str)
