现在的进度:

1.VES:

a. `sessionSetupPrepare(json op_intents)`

创建session (格式化Op-intent, 生成$\mathcal{G_T}$, 最后生成session).

并且返回一个$scon=(\mathsf{session\_content}, \text{Cert}_{\mathcal{V}}^i)​$(异步以后取消这个内容，直接对其他dApp发送$scon​$请求确认)

b. `sessionSetupUpdate(integer session_id, ack)`

投票session

$\mathsf{ack} = [\text{user}, \text{Cert}_{\mathcal{V,D_u}}^i or\ \textcolor{#EE4000}{\text{None}}]​$

c. `sessionSetupFinished(integer session_id)`

结束`sessionSetup` (添加NSB​, stake funds).

向其他dApp发送$(\mathsf{acks}=\mathrm{sorted}(\{\text{Cert}_{\mathcal{V,D_u}}^i\}),\textcolor{#B22222}{\text{Atte}}_{\mathcal{V,D}})=(\mathsf{acks},\text{Cert}(\mathsf{acks};\mathcal{V}))​$

d. 各种`transact...` TODO

2.ISC

a. `CreateContract(`

​	`address[] owner,`

​	` uint[] funds_require,` 

​	`? transactions_intent`

`)`

`transaction_intent`最理想是`json[]`, 可能需要一个新的函数分阶段上传了.

3.dApp



4.其他模块

a. `Class uip.OpIntent`

可扩展的输入检查.

目前的设置:

```python
Key_Attribute_All = ('name', 'op_type')
Key_Attribute_Payment = ('amount', 'src', 'dst')
Key_Attribute_ContractInvocation = ('invoker', 'contract_domain', 'func')
Option_Attribute_Payment = ('unit',)
Option_Attribute_ContractInvocation = ('parameters', 'parameters_description')
Op_Type = ('Payment', 'ContractInvocation')
Chain_Default_Unit = {
    'Ethereum': 'wei'
}
```

使用`createopintents(json op_intents)`就行了.

b. `Class uip.TransactionIntents`

依据已经格式化的`Opintent[]`和`dependencies`初始化Transaction intents和Dependency Graph, 输出是$[\mathrm{Topological\_Sorted}(V_\mathcal{G_T}), \mathsf{dependencies}_\mathcal{G_T}]$.其中$\mathrm{Topological\_Sorted}(V_\mathcal{G_T})$是`Transaction[]`

c. `Class eth.Transaction`

使用`self.jsonize()`返回ethereum可执行的`object Transaction`

依据

使用``

遇到的问题:

1.ISC 的输入问题. solidity只支持一维数组(string, bytes)或者固定的二维数组(bytes[789]\[])

2.ISC 的监视问题. contract如果不在同一个code, 那么并不支持在链上直接交互. 现在由VES暂代ISC进行insurance claim

3.contract invoke的data encode: 要么用户直接提供已经encode过的function-data. 要么必须要一个parament_type_list提供所有变量的类型描述. 这个类型描述有两个作用，一是生成函数签名(例如 `isOwner(address)`)，二是encode data.

4.contract invoke的返回值问题, storage position可以解决问题，这个需要用户提供吗? 也就是contract invocation的op_intent里需要增加一个storage position域

5.VES签名问题，用什么私钥去签?(VES是人?)