现在的进度:

1.VES:

a. `sessionSetupPrepare(json op_intents)`

创建session (格式化$\text{Op-intent}$, 生成$\mathcal{G_T}$, 最后生成session).

并且返回一个$scon=(\mathsf{session\_content}, \text{Cert}_{\mathcal{D}}^i)​$(异步以后取消这个内容，直接对其他dApp发送$scon​$请求确认)

b. `sessionSetupUpdate(integer session_id, ack)`

投票session

$\mathsf{ack} = [\text{user}, \text{Cert}_{\mathcal{D,V_u}}^i]$

遇到的问题:

1.ISC 的输入问题. solidity只支持一维数组(string, bytes)或者固定的二维数组(bytes[789]\[])

2.ISC 的监视问题. contract如果不在同一个code, 那么并不支持在链上直接交互. 现在由VES暂代ISC进行insurance claim

3.contract invoke的data encode: 要么用户直接提供已经encode过的function-data. 要么必须要一个parament_type_list提供所有变量的类型描述. 这个类型描述有两个作用，一是生成函数签名(例如 `isOwner(address)`)，二是encode data.

4.contract invoke的返回值问题, storage position可以解决问题，这个需要用户提供吗? 也就是contract invocation的op_intent里需要增加一个storage position域