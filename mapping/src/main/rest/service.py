from flask_classy import FlaskView, route


class Command(FlaskView):



    @route('/get_results/<string:name>', methods=['GET'])
    def getResults(self, name):
        """
        return current page of results

        :param name:
        :return:
        """
        results = marketSet[name].getResults()
        marketSet[name].webCrawler.next_page()
        return json.dumps(results, cls=Encoder)
