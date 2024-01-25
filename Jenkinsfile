/**
 * A generic pipeline for building a docker image and preparing it for deployment
 * in f5_automation.
 */
def call(body) {
	def config = [:]
	body.resolveStrategy = Closure.DELEGATE_FIRST
	body.delegate = config
	body()

	// set sensible defaults
	config.agentlabel = config.agentlabel ?: 'linux_bbt'
	config.skipCheckout = config.skipCheckout == null ? true : config.skipCheckout

	node(config.agentlabel) {
		try {
			stage ('Clone') {
			    echo "config.skipCheckout: ${config.skipCheckout}"
				if (!config.skipCheckout){
					checkout scm
				} else {
					echo 'Skipping Checkout.'
				}
			}

			stage ('Hello world') {
				 sh "echo 'hello world'"
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

