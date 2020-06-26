import subprocess

class Connector():

    def prepareParameters(self, points, shortest = False, options = None):
        options = options or {}
        profile = "auto_shorter" if shortest else "auto"

        params = dict(
            costing=profile,
            show_locations=True
        )
        params['locations'] = points

        if options:
            params['costing_options'] = {profile: options}

        return params

class ConsoleConnector(Connector):

    def _execute(self, commands):       
        response = ""
        with subprocess.Popen(
            commands,
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ) as proc:
            try:
                for line in iter(proc.stdout.readline, ''):
                    response += line
            except:
                pass
        responsedict = json.loads(response)
    
    def route(self, points, shortest, options):
        params = self.prepareParameters(points, shortest, options)
        response = _execute(["valhalla_run_route", "-j", json.dumps(params)])
        return response




class HttpConnector():
    #TODO
    pass