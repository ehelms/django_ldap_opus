import ldap

from django.conf import settings


def get_ldap_roles(server, username, password):
    timeout = 0
    result_set = []
    
    try:
        ldap_session = ldap.open(server)
        ldap_session.protocol_version = ldap.VERSION3
        
        if settings.REQUIRE_SSL_CERTIFICATE == True:
            ldap_session.start_tls_s()
            ldap_session.set_option(ldap.OPT_X_TLS_DEMAND, True)
        else:
            ldap_session.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        user_dn = "uid=" + username 
        if settings.BIND_DISTINGUISHED_NAME:
            search_string = settings.BIND_DISTINGUISHED_NAME + ',' + settings.BIND_BASE
        else:
            search_string = settings.BIND_BASE
        authentication_string = user_dn + "," + search_string

        ldap_session.simple_bind_s(authentication_string, password)
        
        if settings.GROUP_RETRIEVAL_STRING != '':
            result_id = ldap_session.search(search_string, ldap.SCOPE_SUBTREE, user_dn,[str(settings.GROUP_RETRIEVAL_STRING)])
            while 1:
                result_type, result_data = ldap_session.result(result_id, timeout)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            roles = result_set[0][0][1][str(settings.GROUP_RETRIEVAL_STRING)]
            return roles, ""
        else:
            return {}
    except ldap.INVALID_CREDENTIALS:
        return None, "Invalid credentials"    
    except ldap.LDAPError:
        if type(ldap.LDAPError.message) == dict and ldap.LDAPError.message.has_key('desc'):
            return None, ldap.LDAPError.message['desc']
        else:
            return None, "LDAP Error occurred"
    except e:
        if type(e.message) == dict and e.message.has_key('desc'):
            return None, e.message['desc']
        else:
            return None, "Error occurred"
    finally:
        ldap_session.unbind()
