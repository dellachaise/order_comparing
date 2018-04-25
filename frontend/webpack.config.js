const path = require('path');

module.exports = {  
	mode: 'development',
	devServer: {
  		contentBase: "./src",
	  	proxy: {
			"/api": "http://localhost:8000"
		}
	}
}
