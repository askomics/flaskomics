from deepdiff import DeepDiff


class AskomicsTestCase():
    """AskOmics test case"""

    @staticmethod
    def equal_objects(obj1, obj2):
        """Compare 2 objects"""
        ddiff = DeepDiff(obj1, obj2, ignore_order=True, report_repetition=True)
        if not ddiff == {}:
            print(ddiff)

        return True if ddiff == {} else False
