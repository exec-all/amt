# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This file is a hack and slash implementation of just-enough-wsman
# needed for the commands in amtctrl.
#
# The only python implementation is a set of bindings on openwsman
# library, which is written in C. wsman is just about building /
# parsing XML and sending HTTP requests (with digest auth). Shifting
# out to a C library to do all of this is sub optimal, when this is
# largely built into python. The python openwsman bindings are also
# not straight forward to build, so the code is hard to test, and
# quite non portable.

import uuid

POWER_STATES = {
    'on': 2,
    'off': 8,
    'reboot': 5
}


def get_request(host, resource):
    stub = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
   <s:Header>
       <wsa:Action s:mustUnderstand="true">http://schemas.xmlsoap.org/ws/2004/09/transfer/Get</wsa:Action>
       <wsa:To s:mustUnderstand="true">%(host)s/wsman</wsa:To>
       <wsman:ResourceURI s:mustUnderstand="true">%(resource)s</wsman:ResourceURI>
       <wsa:MessageID s:mustUnderstand="true">uuid:%(uuid)s</wsa:MessageID>
       <wsa:ReplyTo>
           <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
       </wsa:ReplyTo>
   </s:Header>
   <s:Body/>
</s:Envelope>
"""  # noqa
    return stub % {'host': host, 'resource': resource, 'uuid': uuid.uuid4()}


def power_state_request(host, power_state):
    stub = """<?xml version="1.0" encoding="UTF-8"?>
    <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:n1="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService">
    <s:Header>
    <wsa:Action s:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService/RequestPowerStateChange</wsa:Action>
    <wsa:To s:mustUnderstand="true">%(host)s/wsman</wsa:To>
    <wsman:ResourceURI s:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService</wsman:ResourceURI>
    <wsa:MessageID s:mustUnderstand="true">uuid:%(uuid)s</wsa:MessageID>
    <wsa:ReplyTo>
        <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
    </wsa:ReplyTo>
    <wsman:SelectorSet>
       <wsman:Selector Name="Name">Intel(r) AMT Power Management Service</wsman:Selector>
    </wsman:SelectorSet>
    </s:Header>
    <s:Body>
      <n1:RequestPowerStateChange_INPUT>
        <n1:PowerState>%(power_state)d</n1:PowerState>
        <n1:ManagedElement>
          <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
          <wsa:ReferenceParameters>
             <wsman:ResourceURI>http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ComputerSystem</wsman:ResourceURI>
             <wsman:SelectorSet>
                <wsman:Selector wsman:Name="Name">ManagedSystem</wsman:Selector>
             </wsman:SelectorSet>
           </wsa:ReferenceParameters>
         </n1:ManagedElement>
       </n1:RequestPowerStateChange_INPUT>
      </s:Body></s:Envelope>"""  # noqa
    return stub % {'host': host,
                   'power_state': POWER_STATES[power_state],
                   'uuid': uuid.uuid4()}


def change_boot_to_pxe_request(host):
    stub = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:n1="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootConfigSetting">
<s:Header>
<wsa:Action s:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootConfigSetting/ChangeBootOrder</wsa:Action>
<wsa:To s:mustUnderstand="true">%(host)s/wsman</wsa:To>
<wsman:ResourceURI s:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootConfigSetting</wsman:ResourceURI>
<wsa:MessageID s:mustUnderstand="true">uuid:%(uuid)s</wsa:MessageID>
<wsa:ReplyTo>
    <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
</wsa:ReplyTo>
<wsman:SelectorSet>
   <wsman:Selector Name="InstanceID">Intel(r) AMT: Boot Configuration 0</wsman:Selector>
</wsman:SelectorSet>
</s:Header>
<s:Body>
  <n1:ChangeBootOrder_INPUT>
     <n1:Source>
        <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
        <wsa:ReferenceParameters>
            <wsman:ResourceURI>http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootSourceSetting</wsman:ResourceURI>
            <wsman:SelectorSet>
                <wsman:Selector wsman:Name="InstanceID">Intel(r) AMT: Force PXE Boot</wsman:Selector>
            </wsman:SelectorSet>
         </wsa:ReferenceParameters>
     </n1:Source>
   </n1:ChangeBootOrder_INPUT>
</s:Body></s:Envelope>"""  # noqa
    return stub % {'host': host, 'uuid': uuid.uuid4()}


def enable_boot_config_request(host):
    stub = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:n1="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootService">
<s:Header>
<wsa:Action s:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootService/SetBootConfigRole</wsa:Action>
<wsa:To s:mustUnderstand="true">%(host)s/wsman</wsa:To>
<wsman:ResourceURI s:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootService</wsman:ResourceURI>
<wsa:MessageID s:mustUnderstand="true">uuid:%(uuid)s</wsa:MessageID>
<wsa:ReplyTo><wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address></wsa:ReplyTo>
<wsman:SelectorSet>
    <wsman:Selector Name="Name">Intel(r) AMT Boot Service</wsman:Selector>
</wsman:SelectorSet>
</s:Header>
<s:Body>
<n1:SetBootConfigRole_INPUT>
    <n1:BootConfigSetting>
        <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
        <wsa:ReferenceParameters>
             <wsman:ResourceURI>http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootConfigSetting</wsman:ResourceURI>
             <wsman:SelectorSet>
                  <wsman:Selector wsman:Name="InstanceID">Intel(r) AMT: Boot Configuration 0</wsman:Selector>
             </wsman:SelectorSet>
        </wsa:ReferenceParameters>
    </n1:BootConfigSetting>
    <n1:Role>1</n1:Role>
</n1:SetBootConfigRole_INPUT>
</s:Body></s:Envelope>"""  # noqa
    return stub % {'host': host, 'uuid': uuid.uuid4()}



    returns = """<?xml version="1.0" encoding="UTF-8"?>
    <a:Envelope xmlns:a="http://www.w3.org/2003/05/soap-envelope" xmlns:b="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:c="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:d="http://schemas.xmlsoap.org/ws/2005/02/trust" xmlns:e="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:f="http://schemas.dmtf.org/wbem/wsman/1/cimbinding.xsd" xmlns:g="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <a:Header>
    <b:To>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</b:To>
    <b:RelatesTo>uuid:fc505341-1cd4-1cd4-8002-6018dd4b3a84</b:RelatesTo>
    <b:Action a:mustUnderstand="true">http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService/RequestPowerStateChangeResponse</b:Action>
    <b:MessageID>uuid:00000000-8086-8086-8086-00000000004E</b:MessageID>
    <c:ResourceURI>http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService</c:ResourceURI></a:Header><a:Body><g:RequestPowerStateChange_OUTPUT><g:ReturnValue>0</g:ReturnValue></g:RequestPowerStateChange_OUTPUT></a:Body></a:Envelope>"""

    pass

# Local Variables:
# turn off whitespace mode because xml is *so* long
# eval: (whitespace-mode -1)
# End: