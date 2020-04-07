"use strict";

const request = require('request');
const { Pool } = require('pg');
const cron = require("node-cron");

const pool = new Pool({
	user: process.env.USERDB,
	host: process.env.HOSTDB,
	database: process.env.NAMEDB,
	password: process.env.PASSDB,
	port: process.env.PORTDB,
});

const process_exists = "SELECT 1 FROM public.negociospush_process WHERE \"ProcessNumber\" = $1";
const process_insert = "INSERT INTO public.negociospush_process(\"EntityCode\", \"EntityName\", \"EntityNIT\", \"ProcessNumber\", " + 
                       "\"ProcessState\", \"ExecutionCity\", \"IdProcessType\", \"ProcessTypeName\", \"SegmentCode\", \"FamilyCode\", \"ClassCode\", " + 
                       "\"Description\", \"ContractType\", \"LoadDate\", \"SystemLoadDate\", \"Amount\", \"DefinitiveAmount\", \"ProcessStateName\")"+
                       " VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18);";
const delete_old_processes = "DELETE FROM public.negociospush_process WHERE \"SystemLoadDate\" < now() - INTERVAL \'7 days\'";
//console.log(delete_old_processes);

// console.log(options);
function main(){

	console.log("checking api for new processes...");
	var datetime = new Date();
	const limSupFecha = datetime.getDate().toString().padStart(2, "0") + "-" + (datetime.getMonth()+1).toString().padStart(2, "0") + "-" + datetime.getFullYear();
	datetime.setDate(datetime.getDate()-1);
	const limInfFecha = datetime.getDate().toString().padStart(2, "0") + "-" + (datetime.getMonth()+1).toString().padStart(2, "0") + "-" + datetime.getFullYear();
	const id_estado_proceso = '2';
	console.log("limInfFecha = " + limInfFecha);
	console.log("limSupFecha = " + limSupFecha);

	const options = {
		url: 'https://www.contratos.gov.co/administracion/api/Procesos/detalleProceso?limInfFecha=' + limInfFecha + '&limSupFecha=' + limSupFecha + '&id_estado_proceso='+id_estado_proceso+'&tamano=100',
		method: 'GET',
		headers: {
			'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1NXMzckM0cnAzdDQifQ.Y_bn-wolLvuKcQ8yeH5jbUnsTO-OYc-PnhL3HYaoVwk',
			'Content-Type': 'Application/json'
		},
		rejectUnauthorized: false
	}
	
	let values = [''];
	
	request.get(options, function (error, response, body){
		if(error){
			throw error;
		}
		let data = JSON.parse(body);
		datetime = new Date();
		let paginasTotal = data.paginasTotal;
		console.log('paginas:'+paginasTotal + ', cantRegistros:' +  data.cantRegistros);
		console.log('tamano lista'+data.list.length);
		//Primera pagina
		data.list.forEach(function(process) {
			// console.log('Inicia proceso '+ process.numero_constancia);
		 	values = [process.numero_constancia]
		 	//console.log(values);
			pool.query(process_exists, values, (err, res) => {
				if (err) {
					console.log('Error buscando el proceso:' + process.numero_constancia);
			    	console.log(err.stack);
			  	} else {
			  		if(res.rowCount == 0){
				  		// console.log('El proceso no existe en la BD');
			  			values = [process.codi_entidad, process.nomb_entidad, process.nit_entidad, process.numero_constancia,
			  			          process.id_estado_proceso, process.municipios_ejecucion, process.id_tipo_proceso, 
			  			          process.nom_tipo_proceso, process.id_segmento, process.id_familia, process.id_clase,
			  			          process.detalle_objeto_proceso, process.tipo_contrato, process.fecha_carga, datetime,
			  			          process.cuantia_contratar, process.cuantia_def_contratar, process.estado_proceso]
						//Registro no existe, se inserta
						// console.log(values)
						pool.query(process_insert, values, (err, res) => {
							if(err) {
								console.log('Error insertando el proceso:' + process.numero_constancia);
								console.log(err.stack)

							} 
							// else {
								//console.log('se inserta el proceso' + process.numero_constancia);
								// console.log(res)
							// }
						});
			  		} else {
				  		console.log('El proceso '+ process.numero_constancia +' ya existe en la BD se verifica si cambió algún dato');
			  		}
			  	}
			});
		});

		for(let pagina = 2; pagina <= paginasTotal; pagina++)
		{	
			const options2 = {
				url: 'https://www.contratos.gov.co/administracion/api/Procesos/detalleProceso?limInfFecha=' + limInfFecha + '&limSupFecha=' + limSupFecha + '&id_estado_proceso='+id_estado_proceso+'&tamano=100&pagina='+pagina,
				method: 'GET',
				headers: {
					'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1NXMzckM0cnAzdDQifQ.Y_bn-wolLvuKcQ8yeH5jbUnsTO-OYc-PnhL3HYaoVwk',
					'Content-Type': 'Application/json'
				},
				rejectUnauthorized: false
			}	
			request.get(options2, function (error, response, body){
				if(error){
					throw error;
				}
				
				let data = JSON.parse(body);
				console.log('pagina # ' + pagina + '/' + paginasTotal);
				paginasTotal = data.paginasTotal;
				console.log(data.list.length);
				pagina++;
				// Para las paginas 2 en adelante
				data.list.forEach(function(process) {
					//console.log('Inicia proceso');
				 	values = [process.numero_constancia]
				    pool.query(process_exists, values, (err, res) => {
						if (err) {
					    	console.log(err.stack);
					    	console.log('Error buscando el proceso:' + process.numero_constancia);
					  	} else {
					  		if(res.rowCount == 0){
						  		// console.log('El proceso no existe en la BD');
					  			values = [process.codi_entidad, process.nomb_entidad, process.nit_entidad, process.numero_constancia,
					  			          process.id_estado_proceso, process.municipios_ejecucion, process.id_tipo_proceso, 
					  			          process.nom_tipo_proceso, process.id_segmento, process.id_familia, process.id_clase,
					  			          process.detalle_objeto_proceso, process.tipo_contrato, process.fecha_carga, datetime,
					  			          process.cuantia_contratar, process.cuantia_def_contratar, process.estado_proceso]
								//Registro no existe, se inserta
								// console.log(values)
								pool.query(process_insert, values, (err, res) => {
									if(err) {
										console.log(err.stack);
										console.log('Error insertando el proceso:' + process.numero_constancia);
									} 
									// else {
									// 	console.log('se inserta el proceso' + process.numero_constancia);
									//	// console.log(res)
									// }
								});
					  		} else {
						  		console.log('El proceso '+ process.numero_constancia +' ya existe en la BD se verifica si cambió algún dato');
					  		}
					  	}
					});
				});
			});
		}	
	});
}

function deleteRecords(){
	console.log('Se borraran los registros');
	pool.query(delete_old_processes, (err, res) => {
		if(err) {
			console.log(err.stack);
		} else {
			console.log('registros borrados');
		}
	});
}

// schedule tasks to be run on the server
cron.schedule("5 0 * * *", function() {
	console.log("---------------------");
	console.log("Running Cron Job");
	main();
	deleteRecords();
});

