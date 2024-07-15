def verificar_vlan(vlan_id):
    if 1 <= vlan_id <= 1005:
        return "La VLAN corresponde al rango normal."
    elif 1006 <= vlan_id <= 4094:
        return "La VLAN corresponde al rango extendido."
    else:
        return "El número de VLAN no es válido."

vlan_id = int(input("Ingrese el número de VLAN: "))
resultado = verificar_vlan(vlan_id)
print(resultado)
