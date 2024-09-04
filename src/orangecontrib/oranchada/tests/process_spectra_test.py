import unittest
from widgets_pro.process_spectra import ProcessSpectraWidget


class TestLoadSpectraWidget(unittest.TestCase):
    def test_functionality(self):
        # Create an instance of the widget
        widget = ProcessSpectraWidget()

        # Set the input data and parameters
        widget.inputs["Input Data"] = "some_data"
        #widget.parameters["Parameter 1"] = value1
        #widget.parameters["Parameter 2"] = value2

        # Invoke the apply function
        widget.apply()

        # Check that the output data is as expected
        self.assertEqual(widget.outputs["Output Data"], "")

if __name__ == "__main__":
    unittest.main()
