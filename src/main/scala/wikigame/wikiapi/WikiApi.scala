package wikigame.wikiapi

object WikiApi {
  import sttp.client4._

  def sendRequest[F[_]](backend: Backend[F], param: Map[String, String]) =
    basicRequest
      .get(uri"https://en.wikipedia.org/w/api.php?$param")
      .send(backend)
}
