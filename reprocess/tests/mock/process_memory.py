class ProcessMemoryApi:

    @staticmethod
    def get_payload(id):
        return {
            'IdConfiguracaoCenario': '2d4e527c-0a51-4bbf-9141-f8f2a9640e33',
            'IdsUges': [
                'BAUEMC0UG2'
            ]
        }

    @staticmethod
    def get_maps(id):
        return {
            'tipocriterio': {
                'model': 'e_tipocriteriocenario',
                'fields': {
                    'idtipocriterio': {
                        'column': 'id_tipocriteriocenario'
                    },
                    'nometipocriterio': {
                        'column': 'nom_tipocriteriocenario'
                    }
                },
                'filters': {
                    'byIdTipoCriterio': 'id_tipocriteriocenario = :IdTipoCriterio',
                    'byNomeTipoCriterio': 'nom_tipocriteriocenario = :NomeTipoCriterio',
                    'reprocessFilter': 'byNomeTipoCriterio'
                }
            },
            'cenarioeventomudancaestadooperativo': {
                'model': 'e_cenarioeventomudaestdopert',
                'fields': {
                    'idcenarioeventomudancaestadooperativo': {
                        'column': 'id_cenarioeventomudaestdopert'
                    },
                    'idconfiguracaocenario': {
                        'column': 'id_configcenario'
                    },
                    'idusina': {
                        'column': 'id_usi'
                    },
                    'idsamug': {
                        'column': 'id_origemevento'
                    },
                    'numons': {
                        'column': 'num_eventoons'
                    },
                    'iduge': {
                        'column': 'id_uge'
                    },
                    'idagente': {
                        'column': 'id_age'
                    },
                    'dataverificada': {
                        'column': 'dat_verificada'
                    },
                    'potenciadisponivel': {
                        'column': 'val_potdispo'
                    },
                    'statusevento': {
                        'column': 'sts_eventomudaestdopert'
                    },
                    'comentarioagente': {
                        'column': 'dsc_cmnage'
                    },
                    'comentariocosr': {
                        'column': 'dsc_cmncosr'
                    },
                    'idestadooperativo': {
                        'column': 'id_estdopert'
                    },
                    'idcondicaooperativa': {
                        'column': 'id_condicaoopert'
                    },
                    'idclassificacaoorigem': {
                        'column': 'id_origemindispo'
                    },
                    'incluidomanualmente': {
                        'column': 'flg_inclusaomanual'
                    },
                    'alteradodurantefranquia': {
                        'column': 'flg_altfranquia'
                    },
                    'alteradoduranteconsistencia': {
                        'column': 'flg_altconsistencia'
                    },
                    'excluidodurantesuspensao': {
                        'column': 'flg_excsuspensao'
                    },
                    'ideventoorigem': {
                        'column': 'id_eventooriginal'
                    },
                    'versaooficial': {
                        'column': 'ver_oficial'
                    },
                    'versaocenario': {
                        'column': 'ver_cenario'
                    }
                },
                'filters': {
                    'byIdCenario': 'id_configcenario = :IdConfiguracaoCenario'
                }
            },
        }

    @staticmethod
    def get_entities(id):
        return {
            'tipocriterio': [
                {
                    'idtipocriterio': '1966675',
                    'nometipocriterio': 'COSR-NE 09764/2012',
                    'id': '3f84b875-810a-4c06-81d5-96d1185a5b86',
                    '_metadata': {
                        'branch': 'master',
                        'instance_id': '7f77e935-ff13-4ab5-a777-abab64670a91',
                        'modified_at': '2019-11-19T20:48:28.283146',
                        'changeTrack': 'create',
                        'reprocessable': False
                    }
                }
            ],
            'cenarioeventomudancaestadooperativo': [
                {
                    'idsamug': '1966675',
                    'numons': 'COSR-NE 09764/2012',
                    'iduge': 'BAUEMC0UG2',
                    'idagente': 'MAC',
                    'dataverificada': '2012-08-18T15:32:00',
                    'potenciadisponivel': 16.7,
                    'statusevento': 'NCP',
                    'comentarioagente': '[Não Acordado no Prazo SAMUG 8/24/2012 6:04:19 AM]',
                    'dataultimaconsolidacao': '2012-09-15T00:00:00',
                    'idestadooperativo': 'DCO',
                    'idcondicaooperativa': 'NOR',
                    'id': '3f84b875-810a-4c06-81d5-96d1185a5b86',
                    '_metadata': {
                        'branch': 'master',
                        'reprocessable': True
                    }
                },
                {
                    'idcenarioeventomudancaestadooperativo': 'b5ffb49a-a92f-4b32-ac63-045dc52e7dc9',
                    'idconfiguracaocenario': '2d4e527c-0a51-4bbf-9141-f8f2a9640e33',
                    'idusina': 'BAUEMC',
                    'idsamug': '1956035',
                    'numons': 'COSR-NE 08659/2012',
                    'iduge': 'BAUEMC0UG2',
                    'idagente': 'MAC',
                    'dataverificada': '2012-07-06T00:00:00',
                    'potenciadisponivel': 16.7,
                    'statusevento': 'NCP',
                    'comentarioagente': '[Não Acordado no Prazo SAMUG 7/25/2012 6:04:09 AM]',
                    'idestadooperativo': 'EOC',
                    'idcondicaooperativa': 'NOR',
                    'incluidomanualmente': False,
                    'alteradodurantefranquia': False,
                    'alteradoduranteconsistencia': False,
                    'excluidodurantesuspensao': False,
                    'id': 'ad118467-3608-495a-87ef-6130f02174b3',
                    '_metadata': {
                        'branch': 'master',
                        'instance_id': '7f77e935-ff13-4ab5-a777-abab64670a91',
                        'modified_at': '2019-11-19T20:48:28.283146',
                        'changeTrack': 'create',
                        'reprocessable': True
                    }
                },
                {
                    'idcenarioeventomudancaestadooperativo': 'fe7ed634-8701-4656-934d-eded25ec74b4',
                    'idconfiguracaocenario': '2d4e527c-0a51-4bbf-9141-f8f2a9640e33',
                    'idusina': 'BAUEMC',
                    'idsamug': '1956036',
                    'numons': 'COSR-NE 08660/2012',
                    'iduge': 'BAUEMC0UG2',
                    'idagente': 'MAC',
                    'dataverificada': '2012-07-06T00:01:00',
                    'potenciadisponivel': 16.7,
                    'statusevento': 'NCP',
                    'comentarioagente': '[Não Acordado no Prazo SAMUG 7/25/2012 6:04:09 AM]',
                    'idestadooperativo': 'LIG',
                    'idcondicaooperativa': 'NOR',
                    'incluidomanualmente': False,
                    'alteradodurantefranquia': False,
                    'alteradoduranteconsistencia': False,
                    'excluidodurantesuspensao': False,
                    'id': '21f0d55f-a119-4c62-a8b8-fee2ed7cf4ab',
                    '_metadata': {
                        'branch': 'master',
                        'instance_id': '7f77e935-ff13-4ab5-a777-abab64670a91',
                        'modified_at': '2019-11-19T20:48:28.285347',
                        'changeTrack': 'destroy',
                        'reprocessable': True
                    }
                },
                {
                    'idcenarioeventomudancaestadooperativo': 'ae69b83e-036c-4635-af1b-223060c2fb80',
                    'idconfiguracaocenario': '2d4e527c-0a51-4bbf-9141-f8f2a9640e33',
                    'idusina': 'BAUEMC',
                    'idsamug': '1961403',
                    'numons': 'COSR-NE 09047/2012',
                    'iduge': 'BAUEMC0UG2',
                    'idagente': 'MAC',
                    'dataverificada': '2012-08-01T00:00:00',
                    'potenciadisponivel': 16.7,
                    'statusevento': 'NCP',
                    'comentarioagente': '[Não Acordado no Prazo SAMUG 8/8/2012 6:04:12 AM]',
                    'idestadooperativo': 'LIG',
                    'idcondicaooperativa': 'NOR',
                    'incluidomanualmente': False,
                    'alteradodurantefranquia': False,
                    'alteradoduranteconsistencia': False,
                    'excluidodurantesuspensao': False,
                    'id': '01449b43-00ee-4659-8a90-be5edd8804ac',
                    '_metadata': {
                        'branch': 'master',
                        'instance_id': '7f77e935-ff13-4ab5-a777-abab64670a91',
                        'modified_at': '2019-11-19T20:48:28.286006',
                        'changeTrack': 'update',
                        'reprocessable': True
                    }
                }
            ]
        }

    @staticmethod
    def get_using_entities(entities, reprocess_after):
        return [
            '68248eaa-5b21-40ca-9d54-bd082e025381',
            '68248eaa-5b21-40ca-9d54-bd082e025382',
            '68248eaa-5b21-40ca-9d54-bd082e025383',
            '68248eaa-5b21-40ca-9d54-bd082e025384'
        ]

    @staticmethod
    def get_with_entities_type(entities_type, reprocess_after):
        return {
            '68248eaa-5b21-40ca-9d54-bd082e025381',
            '68248eaa-5b21-40ca-9d54-bd082e025382',
            '68248eaa-5b21-40ca-9d54-bd082e025383',
            '68248eaa-5b21-40ca-9d54-bd082e025384',
            '68248eaa-5b21-40ca-9d54-bd082e025385',
            '68248eaa-5b21-40ca-9d54-bd082e025386',
            '68248eaa-5b21-40ca-9d54-bd082e025387',
            '68248eaa-5b21-40ca-9d54-bd082e025388',
        }
