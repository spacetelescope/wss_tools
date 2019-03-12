from wss_tools.utils.io import output_xml


def test_output_xml(tmpdir):
    filename = str(tmpdir.join('simple.xml'))
    xmldict = {'foo': 'bar'}
    output_xml(xmldict, filename)

    with open(filename) as f:
        lines = f.readlines()

    assert len(lines) == 2
    assert lines[0] == '<?xml version="1.0" ?>\n'
    assert lines[1] == '<foo>bar</foo>\n'
