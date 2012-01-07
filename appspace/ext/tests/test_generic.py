def test_suite():
    import doctest
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE,
    )


if __name__ == '__main__':
    import unittest
    r = unittest.TextTestRunner()
    r.run(test_suite())
