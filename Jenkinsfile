def call(body) {
  def config = [:]
  body.resolveStrategy = Closure.DELEGATE_FIRST
  body.delegate = config
  body()

  node ('linux'){
    // Clean workspace before doing anything
    cleanWs()

    try {
      stage ('Clone') {
        checkout scm
      }
      stage ('Executing script') {
        echo "Script will work!!"
			}
		}
		catch (err) {
			currentBuild.result = 'FAILED'
			throw err
		}
		finally {
			cleanWs()
		}
	}
}
